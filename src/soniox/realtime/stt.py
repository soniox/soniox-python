from __future__ import annotations

import json
from collections.abc import Callable, Iterator
from types import TracebackType
from typing import TYPE_CHECKING

from websockets.exceptions import ConnectionClosed

from ..errors import SonioxRealtimeError, SonioxValidationError
from ..types.realtime import RealtimeControlType, RealtimeEvent, RealtimeSTTConfig
from . import _transport
from ._utils import DEFAULT_STT_CONNECTION_POOL_SIZE, KEEP_ALIVE_INTERVAL_SEC, KeepaliveThread, resolve_connect_timeout_sec, ws_connect_kwargs

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

    def __init__(
        self,
        url: str,
        config: RealtimeSTTConfig,
        *,
        connect_timeout_sec: float | None = None,
    ) -> None:
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
            connect_timeout_sec:
                Maximum seconds to wait for the WebSocket handshake to
                complete. ``None`` uses the ``websockets`` library default.
        """
        self._url = url
        self._config = config
        self._connect_timeout_sec = connect_timeout_sec
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
            self._ws = _transport.sync_ws_connect(
                self._url,
                **ws_connect_kwargs(self._connect_timeout_sec),
            )
        except TimeoutError as exc:
            raise SonioxRealtimeError("Connection timed out") from exc
        except Exception as exc:
            raise SonioxRealtimeError("Failed to start realtime session") from exc

        try:
            self._ws.send(json.dumps(self._config.model_dump(exclude_none=True)))
            return self
        except Exception as exc:
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
        Close the realtime session and release the WebSocket.

        Signals end-of-audio to the server and clears the underlying
        connection. Subsequent calls are no-ops.

        Called automatically when exiting the context manager.
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

        Accepts either a single bytes object or an iterator yielding byte
        chunks (e.g. from `throttle_audio`). If `finish=True` (the default),
        an end-of-audio signal is sent after the last chunk; pass
        `finish=False` when you intend to send more audio later in the
        same session.

        Args:
            chunks: Raw bytes or an iterator of byte chunks.
            finish: If True (default), signal end-of-audio after the last chunk.
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
        Signal end-of-audio.

        The server finalizes any pending tokens and closes the
        connection. Continue iterating `receive_events()` to consume
        the remaining tokens.
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

    def pause(self, *, finalize: bool = True) -> None:
        """
        Pause the session, suppressing outgoing audio and starting a
        background keepalive thread.

        While paused, calls to `send_byte_chunk` are silently dropped.
        A background thread sends a keepalive message every
        ``KEEP_ALIVE_INTERVAL_SEC`` seconds to prevent the server from
        timing out the session.

        Calling `pause` on an already-paused session is a no-op.

        Args:
            finalize: If True (default), call `finalize()` before pausing.

        Raises:
            SonioxRealtimeError: If the session is not connected.
        """
        if not self._ws:
            raise SonioxRealtimeError("Realtime session is not connected")
        if self._paused:
            return
        if finalize:
            self.finalize()
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
        self._connection_pool = None

    def _uses_connection_pool(self) -> bool:
        return self._client.stt_connection_pool_size > 0

    def _ensure_connection_pool(self):
        if self._connection_pool is None:
            self._connection_pool = self.create_connection_pool(
                pool_size=self._client.stt_connection_pool_size,
                idle_max_lifetime_sec=self._client.stt_idle_max_lifetime_sec,
                idle_refresh_before_sec=self._client.stt_idle_refresh_before_sec,
            )
        return self._connection_pool

    def warmup_connection_pool(self) -> None:
        """Pre-open idle WebSocket links for upcoming STT sessions."""
        if self._uses_connection_pool():
            self._ensure_connection_pool().warmup()

    def close_connection_pool(self) -> None:
        """Close all idle links in the internal STT connection pool."""
        if self._connection_pool is not None:
            self._connection_pool.close()
            self._connection_pool = None

    def connect(
        self,
        *,
        config: RealtimeSTTConfig,
        api_key: str | None = None,
        connect_timeout_sec: float | None = None,
        use_connection_pool: bool | None = None,
    ) -> RealtimeSTTSession:
        """
        Create a new realtime STT session.

        When ``stt_connection_pool_size`` on the parent client is greater
        than zero (the default is ``5``), the session claims a pre-connected
        WebSocket from the internal pool on enter. Set
        ``stt_connection_pool_size=0`` on the client to disable pooling and
        connect on demand instead.

        The returned session is not connected until entered as a
        context manager.

        Args:
            config:
                Realtime transcription configuration.
            api_key:
                Optional API key override. If not provided, the client's
                default API key is used.
            connect_timeout_sec:
                Maximum seconds to wait for the WebSocket handshake.
                ``None`` uses the client default (also ``None`` by default,
                which keeps the ``websockets`` library default behavior).
            use_connection_pool:
                Override whether to use the internal connection pool.
                ``None`` follows ``stt_connection_pool_size``.

        Returns:
            A new RealtimeSTTSession instance.

        Raises:
            SonioxValidationError:
                If no API key is available.
        """
        key = api_key or self._client.api_key
        if not key:
            raise SonioxValidationError("API key is required to start a realtime session")

        pool_enabled = self._uses_connection_pool() if use_connection_pool is None else use_connection_pool
        if pool_enabled and self._uses_connection_pool():
            from .stt_preconnect import RealtimeSTTPooledSession

            return RealtimeSTTPooledSession(
                self._ensure_connection_pool(),
                config,
                api_key=api_key,
            )

        timeout = resolve_connect_timeout_sec(
            self._client.connect_timeout_sec,
            connect_timeout_sec,
        )

        payload = config.build_payload(key)
        return RealtimeSTTSession(
            self._client.websocket_base_url,
            payload,
            connect_timeout_sec=timeout,
        )

    def connect_idle(
        self,
        *,
        api_key: str | None = None,
        connect_timeout_sec: float | None = None,
    ):
        """
        Open a pre-connected WebSocket link without starting a session.

        Enter the returned connection as a context manager, optionally call
        :meth:`~RealtimeSTTConnection.start_idle_keepalive`, then call
        :meth:`~RealtimeSTTConnection.start_session` when a client is ready.

        Returns:
            A :class:`~soniox.realtime.stt_preconnect.RealtimeSTTConnection`.
        """
        from .stt_preconnect import RealtimeSTTConnection

        key = api_key or self._client.api_key
        if not key:
            raise SonioxValidationError("API key is required to open a realtime connection")

        timeout = resolve_connect_timeout_sec(
            self._client.connect_timeout_sec,
            connect_timeout_sec,
        )
        return RealtimeSTTConnection(
            self._client.websocket_base_url,
            key,
            connect_timeout_sec=timeout,
        )

    def create_connection_pool(
        self,
        *,
        pool_size: int = DEFAULT_STT_CONNECTION_POOL_SIZE,
        api_key: str | None = None,
        connect_timeout_sec: float | None = None,
        idle_keepalive: bool = True,
        keepalive_interval_sec: float | None = None,
        idle_max_lifetime_sec: float | None = None,
        idle_refresh_before_sec: float | None = None,
    ):
        """
        Create a pool of idle WebSocket links (handshake only).

        Idle links send periodic STT keepalive messages but no session config.
        Each link is replaced before ``idle_max_lifetime_sec`` (default 10
        minutes) expires.

        Returns:
            A :class:`~soniox.realtime.stt_preconnect.RealtimeSTTConnectionPool`.
        """
        from ._utils import (
            DEFAULT_IDLE_MAX_LIFETIME_SEC,
            DEFAULT_IDLE_REFRESH_BEFORE_SEC,
            KEEP_ALIVE_INTERVAL_SEC,
        )
        from .stt_preconnect import RealtimeSTTConnectionPool

        key = api_key or self._client.api_key
        if not key:
            raise SonioxValidationError("API key is required to open a realtime connection")

        timeout = resolve_connect_timeout_sec(
            self._client.connect_timeout_sec,
            connect_timeout_sec,
        )
        return RealtimeSTTConnectionPool(
            url=self._client.websocket_base_url,
            api_key=key,
            pool_size=pool_size,
            connect_timeout_sec=timeout,
            idle_keepalive=idle_keepalive,
            keepalive_interval_sec=(
                KEEP_ALIVE_INTERVAL_SEC
                if keepalive_interval_sec is None
                else keepalive_interval_sec
            ),
            idle_max_lifetime_sec=(
                self._client.stt_idle_max_lifetime_sec
                if idle_max_lifetime_sec is None
                else idle_max_lifetime_sec
            ),
            idle_refresh_before_sec=(
                self._client.stt_idle_refresh_before_sec
                if idle_refresh_before_sec is None
                else idle_refresh_before_sec
            ),
        )

    def create_preconnect_pool(
        self,
        *,
        pool_size: int = DEFAULT_STT_CONNECTION_POOL_SIZE,
        api_key: str | None = None,
        connect_timeout_sec: float | None = None,
        idle_keepalive: bool = True,
        keepalive_interval_sec: float | None = None,
        idle_max_lifetime_sec: float | None = None,
        idle_refresh_before_sec: float | None = None,
    ):
        """
        Alias for :meth:`create_connection_pool`.
        """
        return self.create_connection_pool(
            pool_size=pool_size,
            api_key=api_key,
            connect_timeout_sec=connect_timeout_sec,
            idle_keepalive=idle_keepalive,
            keepalive_interval_sec=keepalive_interval_sec,
            idle_max_lifetime_sec=idle_max_lifetime_sec,
            idle_refresh_before_sec=idle_refresh_before_sec,
        )
