from __future__ import annotations

import json
from collections.abc import Callable, Iterator
from types import TracebackType
from typing import TYPE_CHECKING

from websockets.exceptions import ConnectionClosed
from websockets.sync.client import connect as sync_ws_connect

from ..errors import SonioxRealtimeError, SonioxValidationError
from ..types.realtime import RealtimeControlType, RealtimeEvent, RealtimeSTTConfig
from ._utils import KEEP_ALIVE_INTERVAL_SEC, KeepaliveThread

if TYPE_CHECKING:
    from ..client import SonioxClient


class RealtimeSTTSession:
    """
    Synchronous WebSocket session for a single real-time speech-to-text stream.

    This class manages the full lifecycle of a real-time transcription session:
    connecting to the WebSocket endpoint, streaming audio data, receiving events,
    and gracefully closing the stream. A session is stateful and represents
    exactly one streaming interaction with the Soniox realtime API.

    Instances are designed to be used as context managers.
    """

    def __init__(self, url: str, config: RealtimeSTTConfig) -> None:
        """
        Create a new realtime STT session.

        This does not open a network connection. The WebSocket connection
        is established when entering the context manager.

        Args:
            url:
                WebSocket URL for the realtime transcription endpoint.
            config:
                Configuration describing the audio format and transcription
                behavior for this session.
        """
        self._url = url
        self._config = config
        self._ws = None
        self._last_message: RealtimeEvent | None = None
        self._paused = False
        self._keepalive: KeepaliveThread | None = None

    @property
    def config(self) -> RealtimeSTTConfig:
        """
        Return the configuration used to initialize this session.
        """
        return self._config

    @property
    def paused(self) -> bool:
        """Return True if the session is currently paused."""
        return self._paused

    def __enter__(self) -> RealtimeSTTSession:
        """
        Open the WebSocket connection and start the realtime session.

        The session configuration is sent immediately after connecting.
        If any step fails, the connection is closed and a
        SonioxRealtimeError is raised.

        Returns:
            The active realtime session instance.

        Raises:
            SonioxRealtimeError:
                If the WebSocket connection or session initialization fails.
        """
        try:
            self._ws = sync_ws_connect(self._url)
            self._ws.send(json.dumps(self._config.model_dump(exclude_none=True)))
            return self
        except Exception as exc:
            # Cleanup on failure
            if self._ws:
                try:
                    self._ws.close()
                except Exception:
                    pass
                self._ws = None
            raise SonioxRealtimeError("Failed to start realtime session") from exc

    def __exit__(
        self,
        _exc_type: type[BaseException] | None,
        _exc_value: BaseException | None,
        _traceback: TracebackType | None,
    ) -> None:
        """
        Close the realtime session and release network resources.

        This method is called automatically when exiting the
        context manager.
        """
        _ = (_exc_type, _exc_value, _traceback)  # To make linter happy.
        self.close()

    def close(self) -> None:
        """
        Gracefully close the realtime session.

        Sends a final empty message to signal end-of-stream, then closes
        the WebSocket connection. Calling this method multiple times is safe.
        """
        if self._keepalive is not None:
            self._keepalive.stop()
            self._keepalive = None
        self._paused = False
        if not self._ws:
            return
        try:
            self._ws.send("")
        except ConnectionClosed:
            pass
        except Exception:
            self._ws.close()
        finally:
            self._ws = None

    def send_byte_chunk(self, chunk: bytes) -> None:
        """
        Send a single chunk of raw audio bytes to the realtime stream.

        The audio data must match the format declared in the session
        configuration (sample rate, channels, encoding).

        Args:
            chunk:
                Raw audio bytes to send.

        Raises:
            SonioxRealtimeError:
                If the session is not connected or the send operation fails.
        """
        if not self._ws:
            raise SonioxRealtimeError("Realtime session is not connected")
        if self._paused:
            return
        try:
            self._ws.send(chunk)
        except Exception as exc:
            raise SonioxRealtimeError("Failed to send audio chunk") from exc

    def send_bytes(self, chunks: bytes | Iterator[bytes], *, finish: bool = True) -> None:
        """
        Send audio data to the realtime stream.

        This method accepts either a single bytes object or an iterator
        yielding audio chunks. When an iterator is provided, a FINISH
        control message is sent automatically after all chunks have
        been transmitted.

        Args:
            chunks:
                Audio data as raw bytes or an iterator of byte chunks.
        """
        if isinstance(chunks, bytes):
            self.send_byte_chunk(chunks)
            return

        for chunk in chunks:
            self.send_byte_chunk(chunk)

        if finish:
            self.finish()

    def send_control_message(self, control_type: RealtimeControlType) -> None:
        """
        Send a control message to the realtime session.

        Control messages modify the state of the stream, such as signaling
        end-of-audio or requesting finalization.

        Args:
            control_type:
                The type of control message to send.

        Raises:
            SonioxRealtimeError:
                If the session is not connected or the message cannot be sent.
        """
        if not self._ws:
            raise SonioxRealtimeError("Realtime session is not connected")
        try:
            if control_type == RealtimeControlType.FINISH:
                self._ws.send("")
            elif control_type == RealtimeControlType.KEEP_ALIVE:
                self._ws.send(json.dumps({"type": "keepalive"}))
            elif control_type == RealtimeControlType.FINALIZE:
                self._ws.send(json.dumps({"type": "finalize"}))
        except Exception as exc:
            raise SonioxRealtimeError("Failed to send control message") from exc

    def finish(self) -> None:
        """
        Signal that no more audio will be sent for this session.
        """
        self.send_control_message(RealtimeControlType.FINISH)

    def keep_alive(self) -> None:
        """
        Send a keep-alive message to prevent the session from timing out.
        """
        self.send_control_message(RealtimeControlType.KEEP_ALIVE)

    def finalize(self) -> None:
        """
        Finalize all outstanding non-final tokens while keeping the session open.

        Subsequent tokens will be delivered with `is_final=True`.
        """
        self.send_control_message(RealtimeControlType.FINALIZE)

    def recv_bytes(self) -> bytes:
        """
        Receive a raw message from the WebSocket connection.

        Returns:
            The received message as bytes. An empty bytes object indicates
            that the connection has been closed.
        """
        if not self._ws:
            raise SonioxRealtimeError("Realtime session is not connected")
        try:
            message = self._ws.recv()
        except ConnectionClosed:
            return b""
        if isinstance(message, str):
            return message.encode("utf-8")
        return message

    def parse_event(self, raw: str | bytes) -> RealtimeEvent:
        """
        Parse a raw WebSocket message into a structured realtime event.

        Args:
            raw:
                Raw message payload received from the server.

        Returns:
            A validated RealtimeEvent instance.
        """
        return RealtimeEvent.validate_event(raw)

    @property
    def last_message(self) -> RealtimeEvent | None:
        """
        Return the most recently received realtime event, if any.
        """
        return self._last_message

    def receive_event(self) -> RealtimeEvent | None:
        """
        Receive and parse the next realtime event from the server.

        Returns:
            The next RealtimeEvent, or None if the connection has closed.

        Raises:
            SonioxRealtimeError:
                If the session is not connected.
        """
        if not self._ws:
            raise SonioxRealtimeError("Realtime session is not connected")
        raw = self.recv_bytes()
        if not raw:
            return None
        event = self.parse_event(raw)
        self._last_message = event
        return event

    def receive_events(self) -> Iterator[RealtimeEvent]:
        """
        Yield realtime events as they are received from the server.

        Iteration stops automatically when the connection is closed.
        """
        while True:
            event = self.receive_event()
            if event is None:
                break
            yield event

    def handle_events(self, handler: Callable[[RealtimeEvent], None]) -> None:
        """
        Receive realtime events and dispatch them to a handler callback.

        Args:
            handler:
                Callable invoked for each received RealtimeEvent.
        """
        for event in self.receive_events():
            handler(event)

    def pause(self) -> None:
        """
        Pause the session, suppressing outgoing audio and starting a
        background keepalive thread.

        While paused, calls to :meth:`send_byte_chunk` are silently dropped.
        A background thread sends a keepalive message every
        ``KEEP_ALIVE_INTERVAL_SEC`` seconds to prevent the server from
        timing out the session.

        Calling `pause` on an already-paused session is a no-op.

        Raises:
            SonioxRealtimeError: If the session is not connected.
        """
        if not self._ws:
            raise SonioxRealtimeError("Realtime session is not connected")
        if self._paused:
            return
        self._paused = True
        self._keepalive = KeepaliveThread(self.keep_alive, KEEP_ALIVE_INTERVAL_SEC)
        self._keepalive.start()

    def resume(self) -> None:
        """
        Resume a paused session, stopping the keepalive thread and
        allowing audio to be sent again.

        Calling `resume` on a session that is not paused is a no-op.

        Raises:
            SonioxRealtimeError: If the session is not connected.
        """
        if not self._ws:
            raise SonioxRealtimeError("Realtime session is not connected")
        if not self._paused:
            return
        if self._keepalive is not None:
            self._keepalive.stop()
            self._keepalive = None
        self._paused = False

    enter = __enter__


class RealtimeSTTClient:
    """
    Factory for creating synchronous realtime speech-to-text sessions.

    This class validates credentials and prepares session configuration,
    but does not itself manage WebSocket connections.
    """

    def __init__(self, client: SonioxClient) -> None:
        """
        Create a realtime STT client bound to an existing API client.

        Args:
            client:
                Parent Soniox client providing configuration and credentials.
        """
        self._client = client

    def connect(
        self,
        *,
        config: RealtimeSTTConfig,
        api_key: str | None = None,
    ) -> RealtimeSTTSession:
        """
        Create a new realtime STT session.

        The returned session is not connected until entered as a
        context manager.

        Args:
            config:
                Realtime transcription configuration.
            api_key:
                Optional API key override. If not provided, the client's
                default API key is used.

        Returns:
            A new RealtimeSTTSession instance.

        Raises:
            SonioxValidationError:
                If no API key is available.
        """
        key = api_key or self._client.api_key
        if not key:
            raise SonioxValidationError("API key is required to start a realtime session")

        payload = config.build_payload(key)
        return RealtimeSTTSession(
            self._client.websocket_base_url,
            payload,
        )
