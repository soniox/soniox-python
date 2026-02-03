from __future__ import annotations

import json
from collections.abc import AsyncIterator, Awaitable, Callable
from types import TracebackType
from typing import TYPE_CHECKING

from websockets import connect as async_ws_connect
from websockets.exceptions import ConnectionClosed

from ..errors import SonioxRealtimeError, SonioxValidationError
from ..types.realtime import RealtimeControlType, RealtimeEvent, RealtimeSTTConfig

if TYPE_CHECKING:
    from ..client import AsyncSonioxClient


class AsyncRealtimeSTTSession:
    """
    Asynchronous WebSocket session for a single real-time speech-to-text stream.

    This class manages the full lifecycle of a real-time transcription session:
    connecting to the WebSocket endpoint, streaming audio data, receiving events,
    and gracefully closing the stream. A session is stateful and represents
    exactly one streaming interaction with the Soniox realtime API.

    Instances are designed to be used as async context managers.
    """

    def __init__(self, url: str, config: RealtimeSTTConfig) -> None:
        """
        Create a new realtime STT session.

        This does not open a network connection. The WebSocket connection
        is established when entering the async context manager.

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

    @property
    def config(self) -> RealtimeSTTConfig:
        """
        Return the configuration used to initialize this session.
        """
        return self._config

    async def __aenter__(self) -> AsyncRealtimeSTTSession:
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
            self._ws = await async_ws_connect(self._url)
            await self._ws.send(json.dumps(self._config.model_dump(exclude_none=True)))
            return self
        except Exception as exc:
            if self._ws:
                try:
                    await self._ws.close()
                except Exception:
                    pass
                self._ws = None
            raise SonioxRealtimeError("Failed to start realtime session") from exc

    async def __aexit__(
        self,
        _exc_type: type[BaseException] | None,
        _exc_value: BaseException | None,
        _traceback: TracebackType | None,
    ) -> None:
        """
        Close the realtime session and release network resources.

        This method is called automatically when exiting the async
        context manager.
        """
        _ = (_exc_type, _exc_value, _traceback)  # To make linter happy.
        await self.close()

    async def close(self) -> None:
        """
        Gracefully close the realtime session.

        Sends a final empty message to signal end-of-stream, then closes
        the WebSocket connection. Calling this method multiple times is safe.
        """
        if not self._ws:
            return
        try:
            await self._ws.send("")
        except ConnectionClosed:
            pass
        except Exception:
            await self._ws.close()
        finally:
            self._ws = None

    async def send_byte_chunk(self, chunk: bytes) -> None:
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
        try:
            await self._ws.send(chunk)
        except Exception as exc:
            raise SonioxRealtimeError("Failed to send audio chunk") from exc

    async def send_bytes(self, chunks: bytes | AsyncIterator[bytes]) -> None:
        """
        Send audio data to the realtime stream.

        This method accepts either a single bytes object or an iterator
        yielding audio chunks. When an iterator is provided, a
        FINISH control message is sent automatically after all chunks
        have been transmitted.

        Args:
            chunks:
                Audio data as raw bytes or an iterator of byte chunks.
        """
        if isinstance(chunks, bytes):
            await self.send_byte_chunk(chunks)
            return

        async for chunk in chunks:
            await self.send_byte_chunk(chunk)
        await self.send_finish()

    async def send_control_message(self, control_type: RealtimeControlType) -> None:
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
                await self._ws.send("")
            elif control_type == RealtimeControlType.KEEP_ALIVE:
                await self._ws.send(json.dumps({"type": "keepalive"}))
            elif control_type == RealtimeControlType.FINALIZE:
                await self._ws.send(json.dumps({"type": "finalize"}))
        except Exception as exc:
            raise SonioxRealtimeError("Failed to send control message") from exc

    async def send_finish(self) -> None:
        """
        Signal that no more audio will be sent for this session.
        """
        await self.send_control_message(RealtimeControlType.FINISH)

    async def send_keep_alive(self) -> None:
        """
        Send a keep-alive message to prevent the session from timing out.
        """
        await self.send_control_message(RealtimeControlType.KEEP_ALIVE)

    async def send_finalize(self) -> None:
        """
        Finalize all outstanding non-final tokens while keeping the session open.

        Subsequent tokens will be delivered with `is_final=True`.
        """
        await self.send_control_message(RealtimeControlType.FINALIZE)

    async def recv_bytes(self) -> bytes:
        """
        Receive a raw message from the WebSocket connection.

        Returns:
            The received message as bytes. An empty bytes object indicates
            that the connection has been closed.
        """
        if not self._ws:
            raise SonioxRealtimeError("Realtime session is not connected")
        try:
            message = await self._ws.recv()
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

    async def receive_event(self) -> RealtimeEvent | None:
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
        raw = await self.recv_bytes()
        if not raw:
            return None
        event = self.parse_event(raw)
        self._last_message = event
        return event

    async def receive_events(self) -> AsyncIterator[RealtimeEvent]:
        """
        Yield realtime events as they are received from the server.

        Iteration stops automatically when the connection is closed.
        """
        while True:
            event = await self.receive_event()
            if event is None:
                break
            yield event

    async def handle_events(self, handler: Callable[[RealtimeEvent], Awaitable[None]]) -> None:
        """
        Receive realtime events and dispatch them to a handler callback.

        Args:
            handler:
                Callable invoked for each received RealtimeEvent.
        """
        async for event in self.receive_events():
            await handler(event)

    enter = __aenter__
    aenter = __aenter__


class AsyncRealtimeSTTClient:
    """
    Factory for creating asynchronous realtime speech-to-text sessions.

    This class validates credentials and prepares session configuration,
    but does not itself manage WebSocket connections.
    """

    def __init__(self, client: AsyncSonioxClient) -> None:
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
    ) -> AsyncRealtimeSTTSession:
        """
        Create a new realtime STT session.

        The returned session is not connected until entered as an async
        context manager.

        Args:
            config:
                Realtime transcription configuration.
            api_key:
                Optional API key override. If not provided, the client's
                default API key is used.

        Returns:
            A new AsyncRealtimeSTTSession instance.

        Raises:
            SonioxValidationError:
                If no API key is available.
        """
        key = api_key or self._client.api_key
        if not key:
            raise SonioxValidationError("API key is required to start a realtime session")

        payload = config.build_payload(key)
        return AsyncRealtimeSTTSession(
            self._client.websocket_base_url,
            payload,
        )
