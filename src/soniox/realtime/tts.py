from __future__ import annotations

import json
import threading
import time
from collections import deque
from collections.abc import Iterator
from types import TracebackType
from typing import TYPE_CHECKING, Any

from websockets.exceptions import ConnectionClosed
from websockets.sync.client import connect as sync_ws_connect

from ..errors import SonioxRealtimeError, SonioxValidationError
from ..types.realtime import (
    RealtimeTTSCancelMessage,
    RealtimeTTSConfig,
    RealtimeTTSEvent,
    RealtimeTTSKeepAliveMessage,
    RealtimeTTSTextMessage,
)
from ._constants import (
    MAX_TTS_STREAMS_PER_CONNECTION,
    TTS_KEEP_ALIVE_INTERVAL_SEC,
    TTS_STREAM_EVENT_TIMEOUT_SEC,
)
from ._utils import DEFAULT_CONNECT_TIMEOUT_SEC, KeepaliveThread, validate_connect_timeout_sec

if TYPE_CHECKING:
    from ..client import SonioxClient


class RealtimeTTSConnection:
    """Synchronous WebSocket connection for one realtime Text-to-Speech stream."""

    def __init__(
        self,
        url: str,
        config: RealtimeTTSConfig,
        *,
        connect_timeout_sec: float = DEFAULT_CONNECT_TIMEOUT_SEC,
    ) -> None:
        self._url = url
        self._config = config
        self._connect_timeout_sec = connect_timeout_sec
        self._ws = None
        self._last_message: RealtimeTTSEvent | None = None
        self._paused = False
        self._keepalive: KeepaliveThread | None = None

    @property
    def config(self) -> RealtimeTTSConfig:
        """Configuration used to initialize this connection."""
        return self._config

    @property
    def paused(self) -> bool:
        """Return True if the connection is currently paused."""
        return self._paused

    def __enter__(self) -> RealtimeTTSConnection:
        """Open the websocket and start the realtime stream."""
        try:
            self._ws = sync_ws_connect(
                self._url,
                open_timeout=self._connect_timeout_sec,
            )
        except TimeoutError as exc:
            raise SonioxRealtimeError("Connection timed out") from exc
        except Exception as exc:
            raise SonioxRealtimeError("Failed to start realtime Text-to-Speech connection") from exc

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
            raise SonioxRealtimeError("Failed to start realtime Text-to-Speech connection") from exc

    def __exit__(
        self,
        _exc_type: type[BaseException] | None,
        _exc_value: BaseException | None,
        _traceback: TracebackType | None,
    ) -> None:
        _ = (_exc_type, _exc_value, _traceback)  # To make linter happy.
        self.close()

    def close(self) -> None:
        """Close the realtime Text-to-Speech connection."""
        if self._keepalive is not None:
            self._keepalive.stop()
            self._keepalive = None
        self._paused = False
        if not self._ws:
            return
        self._ws.close()
        self._ws = None

    def send_text_chunk(self, text: str, *, text_end: bool = False) -> None:
        """Send one text chunk to the realtime stream."""
        if not self._ws:
            raise SonioxRealtimeError("Realtime Text-to-Speech is not connected")
        if self._paused:
            return
        payload = RealtimeTTSTextMessage(
            text=text,
            text_end=text_end,
            stream_id=self._config.stream_id,
        )
        try:
            self._ws.send(json.dumps(payload.model_dump()))
        except Exception as exc:
            raise SonioxRealtimeError("Failed to send text chunk") from exc

    def send_text_chunks(self, chunks: str | Iterator[str], *, text_end: bool = True) -> None:
        """Send text data to the realtime stream."""
        if isinstance(chunks, str):
            self.send_text_chunk(chunks, text_end=text_end)
            return

        for chunk in chunks:
            self.send_text_chunk(chunk, text_end=False)
        if text_end:
            self.finish()

    def finish(self) -> None:
        """Signal that no more text will be sent for this stream."""
        self.send_text_chunk("", text_end=True)

    def cancel(self) -> None:
        """Cancel the realtime Text-to-Speech stream."""
        if not self._ws:
            raise SonioxRealtimeError("Realtime Text-to-Speech is not connected")
        payload = RealtimeTTSCancelMessage(stream_id=self._config.stream_id, cancel=True)
        try:
            self._ws.send(json.dumps(payload.model_dump()))
        except Exception as exc:
            raise SonioxRealtimeError("Failed to cancel Text-to-Speech stream") from exc

    def keep_alive(self) -> None:
        """
        Send a keep-alive message to prevent the session from timing out.
        """
        if not self._ws:
            raise SonioxRealtimeError("Realtime Text-to-Speech is not connected")
        payload = RealtimeTTSKeepAliveMessage()
        try:
            self._ws.send(json.dumps(payload.model_dump()))
        except Exception as exc:
            raise SonioxRealtimeError("Failed to send keep-alive message") from exc

    def pause(self) -> None:
        """Pause outgoing text and start periodic keep-alive messages."""
        if not self._ws:
            raise SonioxRealtimeError("Realtime Text-to-Speech is not connected")
        if self._paused:
            return
        interval_sec = TTS_KEEP_ALIVE_INTERVAL_SEC
        if interval_sec <= 0:
            raise SonioxValidationError("keep-alive interval must be greater than 0")
        if self._keepalive is not None:
            return
        self._paused = True
        self._keepalive = KeepaliveThread(self.keep_alive, interval_sec)
        self._keepalive.start()

    def resume(self) -> None:
        """Resume outgoing text and stop periodic keep-alive messages."""
        if not self._ws:
            raise SonioxRealtimeError("Realtime Text-to-Speech is not connected")
        if not self._paused:
            return
        if self._keepalive is not None:
            self._keepalive.stop()
            self._keepalive = None
        self._paused = False

    def recv_bytes(self) -> bytes:
        """Receive one raw websocket message payload as bytes."""
        if not self._ws:
            raise SonioxRealtimeError("Realtime Text-to-Speech is not connected")
        try:
            message = self._ws.recv(timeout=TTS_STREAM_EVENT_TIMEOUT_SEC)
        except ConnectionClosed:
            return b""
        except TimeoutError as exc:
            raise SonioxRealtimeError(
                "Timed out waiting for realtime Text-to-Speech event"
            ) from exc
        if isinstance(message, str):
            return message.encode("utf-8")
        return message

    def parse_event(self, raw: str | bytes) -> RealtimeTTSEvent:
        """Parse a raw websocket message into a realtime event."""
        return RealtimeTTSEvent.validate_event(raw)

    def receive_event(self) -> RealtimeTTSEvent | None:
        """Receive and parse the next realtime event."""
        if not self._ws:
            raise SonioxRealtimeError("Realtime Text-to-Speech is not connected")
        raw = self.recv_bytes()
        if not raw:
            return None
        event = self.parse_event(raw)
        self._last_message = event
        if event.error_code is not None:
            message = event.error_message or "Realtime Text-to-Speech stream failed"
            raise SonioxRealtimeError(f"{message} (code {event.error_code})")
        return event

    @property
    def last_message(self) -> RealtimeTTSEvent | None:
        """Most recently received realtime event, if any."""
        return self._last_message

    def receive_events(self) -> Iterator[RealtimeTTSEvent]:
        """Yield realtime events until the stream ends or closes."""
        while True:
            event = self.receive_event()
            if event is None:
                break
            yield event
            if event.terminated:
                break

    def receive_audio_chunks(self) -> Iterator[bytes]:
        """Yield decoded audio chunks from incoming realtime events."""
        for event in self.receive_events():
            try:
                chunk = event.audio_bytes()
            except ValueError as exc:
                raise SonioxRealtimeError("Invalid realtime Text-to-Speech audio payload") from exc
            if chunk is not None:
                yield chunk
            if event.terminated:
                break


class RealtimeTTSClient:
    """Factory for synchronous realtime Text-to-Speech connections and streams."""

    def __init__(self, client: SonioxClient) -> None:
        self._client = client

    def connect(
        self,
        *,
        config: RealtimeTTSConfig,
        api_key: str | None = None,
        connect_timeout_sec: float = DEFAULT_CONNECT_TIMEOUT_SEC,
    ) -> RealtimeTTSConnection:
        """Create a single-stream realtime Text-to-Speech connection."""
        key = api_key or self._client.api_key
        if not key:
            raise SonioxValidationError(
                "API key is required to start a realtime Text-to-Speech connection"
            )
        timeout_sec = validate_connect_timeout_sec(connect_timeout_sec)
        payload = config.build_payload(key)
        return RealtimeTTSConnection(
            self._client.tts_websocket_base_url,
            payload,
            connect_timeout_sec=timeout_sec,
        )

    def connect_multi_stream(
        self,
        *,
        connect_timeout_sec: float = DEFAULT_CONNECT_TIMEOUT_SEC,
    ) -> RealtimeTTSMultiplexedConnection:
        """Create a multiplexed realtime Text-to-Speech connection."""
        key = self._client.api_key
        if not key:
            raise SonioxValidationError(
                "API key is required to start a realtime Text-to-Speech connection"
            )
        timeout_sec = validate_connect_timeout_sec(connect_timeout_sec)
        return RealtimeTTSMultiplexedConnection(
            self._client.tts_websocket_base_url,
            key,
            connect_timeout_sec=timeout_sec,
        )


class RealtimeTTSMultiplexedConnection:
    """Synchronous websocket connection that can host multiple Text-to-Speech streams."""

    def __init__(
        self,
        url: str,
        api_key: str,
        *,
        connect_timeout_sec: float = DEFAULT_CONNECT_TIMEOUT_SEC,
    ) -> None:
        self._url = url
        self._api_key = api_key
        self._connect_timeout_sec = connect_timeout_sec
        self._ws = None
        self._events_by_stream: dict[str, deque[RealtimeTTSEvent]] = {}
        self._active_stream_ids: set[str] = set()
        self._last_message: RealtimeTTSEvent | None = None
        self._paused = False
        self._receive_lock = threading.Lock()
        self._send_lock = threading.Lock()
        self._keepalive: KeepaliveThread | None = None

    @property
    def last_message(self) -> RealtimeTTSEvent | None:
        """Most recently received realtime event, if any."""
        return self._last_message

    @property
    def paused(self) -> bool:
        """Return True if the connection is currently paused."""
        return self._paused

    def __enter__(self) -> RealtimeTTSMultiplexedConnection:
        """Open the shared websocket connection."""
        try:
            self._ws = sync_ws_connect(
                self._url,
                open_timeout=self._connect_timeout_sec,
            )
            return self
        except TimeoutError as exc:
            raise SonioxRealtimeError("Connection timed out") from exc
        except Exception as exc:
            raise SonioxRealtimeError("Failed to start realtime Text-to-Speech connection") from exc

    def __exit__(
        self,
        _exc_type: type[BaseException] | None,
        _exc_value: BaseException | None,
        _traceback: TracebackType | None,
    ) -> None:
        _ = (_exc_type, _exc_value, _traceback)  # To make linter happy.
        self.close()

    def close(self) -> None:
        """Close the websocket and clear the stream state."""
        if self._keepalive is not None:
            self._keepalive.stop()
            self._keepalive = None
        self._paused = False
        if not self._ws:
            return
        try:
            self._ws.close()
        finally:
            self._ws = None
            self._active_stream_ids.clear()
            self._events_by_stream.clear()

    def _send_json(self, payload: dict[str, Any]) -> None:
        """Send a JSON payload on the shared websocket."""
        if not self._ws:
            raise SonioxRealtimeError("Realtime Text-to-Speech connection is not connected")
        try:
            with self._send_lock:
                self._ws.send(json.dumps(payload))
        except Exception as exc:
            raise SonioxRealtimeError("Failed to send Text-to-Speech message") from exc

    def keep_alive(self) -> None:
        """
        Send a keep-alive message to prevent the session from timing out.
        """
        self._send_json(RealtimeTTSKeepAliveMessage().model_dump())

    def pause(self) -> None:
        """Pause outgoing text and start periodic keep-alive messages."""
        if not self._ws:
            raise SonioxRealtimeError("Realtime Text-to-Speech connection is not connected")
        if self._paused:
            return
        interval_sec = TTS_KEEP_ALIVE_INTERVAL_SEC
        if interval_sec <= 0:
            raise SonioxValidationError("keepalive interval must be greater than 0")
        if self._keepalive is not None:
            return
        self._paused = True
        self._keepalive = KeepaliveThread(self.keep_alive, interval_sec)
        self._keepalive.start()

    def resume(self) -> None:
        """Resume outgoing text and stop periodic keep-alive messages."""
        if not self._ws:
            raise SonioxRealtimeError("Realtime Text-to-Speech connection is not connected")
        if not self._paused:
            return
        if self._keepalive is not None:
            self._keepalive.stop()
            self._keepalive = None
        self._paused = False

    def open_stream(self, *, config: RealtimeTTSConfig) -> RealtimeTTSStream:
        """Register and start a new stream on the shared websocket."""
        if not self._ws:
            raise SonioxRealtimeError("Realtime Text-to-Speech connection is not connected")
        stream_id = config.stream_id
        if stream_id in self._active_stream_ids:
            raise SonioxRealtimeError(f"Stream '{stream_id}' is already active on this connection")
        if len(self._active_stream_ids) >= MAX_TTS_STREAMS_PER_CONNECTION:
            raise SonioxRealtimeError(
                f"Maximum concurrent streams ({MAX_TTS_STREAMS_PER_CONNECTION}) reached"
            )
        payload = config.build_payload(self._api_key)
        payload_dict = payload.model_dump(exclude_none=True)
        # Opening a stream is done by sending its config first.
        self._send_json(payload_dict)
        self._active_stream_ids.add(stream_id)
        # Buffer will hold future events for this stream_id.
        self._events_by_stream.setdefault(stream_id, deque())
        return RealtimeTTSStream(self, config)

    def _recv_next_event(self, *, timeout_sec: float | None = None) -> RealtimeTTSEvent | None:
        """Receive and parse the next event from the shared websocket."""
        if not self._ws:
            raise SonioxRealtimeError("Realtime Text-to-Speech connection is not connected")
        try:
            message = self._ws.recv(timeout=timeout_sec)
        except ConnectionClosed:
            return None
        except TimeoutError as exc:
            raise SonioxRealtimeError(
                "Timed out waiting for realtime Text-to-Speech event"
            ) from exc
        raw = message.encode("utf-8") if isinstance(message, str) else message
        event = RealtimeTTSEvent.validate_event(raw)
        self._last_message = event
        return event

    def _take_buffered_event(self, stream_id: str) -> RealtimeTTSEvent | None:
        """Pop the next queued event for ``stream_id``, if available."""
        queue = self._events_by_stream.get(stream_id)
        if queue:
            return queue.popleft()
        return None

    def _route_event(self, event: RealtimeTTSEvent) -> None:
        """Route an event into its per-stream queue."""
        if event.stream_id is not None:
            self._events_by_stream.setdefault(event.stream_id, deque()).append(event)

    def _receive_event_for_stream(self, stream_id: str) -> RealtimeTTSEvent | None:
        """Receive the next event for ``stream_id`` from the shared connection."""
        deadline = time.monotonic() + TTS_STREAM_EVENT_TIMEOUT_SEC
        with self._receive_lock:
            event = self._take_buffered_event(stream_id)
            if event is not None:
                return event
            while True:
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    raise SonioxRealtimeError(
                        f"Timed out waiting for event for stream '{stream_id}'"
                    )
                event = self._recv_next_event(timeout_sec=remaining)
                if event is None:
                    return None
                if event.stream_id is None:
                    if event.error_code is not None:
                        message = event.error_message or "Realtime Text-to-Speech stream failed"
                        raise SonioxRealtimeError(f"{message} (code {event.error_code})")
                    continue
                self._route_event(event)
                if event.stream_id == stream_id:
                    return self._take_buffered_event(stream_id)

    def _deactivate_stream(self, stream_id: str) -> None:
        """Mark a stream as no longer active."""
        self._active_stream_ids.discard(stream_id)


class RealtimeTTSStream:
    """Handle for one stream on a multiplexed realtime TTS connection."""

    def __init__(
        self, connection: RealtimeTTSMultiplexedConnection, config: RealtimeTTSConfig
    ) -> None:
        self._connection = connection
        self._config = config
        self._last_message: RealtimeTTSEvent | None = None

    @property
    def config(self) -> RealtimeTTSConfig:
        """Stream configuration."""
        return self._config

    @property
    def stream_id(self) -> str:
        """Stream identifier."""
        return self._config.stream_id

    @property
    def last_message(self) -> RealtimeTTSEvent | None:
        """Most recently received event for this stream, if any."""
        return self._last_message

    def send_text_chunk(self, text: str, *, text_end: bool = False) -> None:
        """Send one text chunk for this stream."""
        if self._connection.paused:
            return
        payload = RealtimeTTSTextMessage(
            text=text,
            text_end=text_end,
            stream_id=self._config.stream_id,
        )
        self._connection._send_json(payload.model_dump())  # pyright: ignore[reportPrivateUsage]

    def send_text_chunks(self, chunks: str | Iterator[str], *, text_end: bool = True) -> None:
        """Send text chunks for this stream."""
        if isinstance(chunks, str):
            self.send_text_chunk(chunks, text_end=text_end)
            return
        for chunk in chunks:
            self.send_text_chunk(chunk, text_end=False)
        if text_end:
            self.finish()

    def finish(self) -> None:
        """Signal that no more text will be sent for this stream."""
        self.send_text_chunk("", text_end=True)

    def cancel(self) -> None:
        """Cancel this stream."""
        payload = RealtimeTTSCancelMessage(stream_id=self._config.stream_id)
        self._connection._send_json(payload.model_dump())  # pyright: ignore[reportPrivateUsage]

    def keep_alive(self) -> None:
        """Send a keepalive message on the underlying shared connection."""
        self._connection.keep_alive()

    def pause(self) -> None:
        """Pause the underlying shared connection and start keepalive."""
        self._connection.pause()

    def resume(self) -> None:
        """Resume the underlying shared connection and stop keepalive."""
        self._connection.resume()

    def receive_event(self) -> RealtimeTTSEvent | None:
        """Receive the next event for this stream."""
        event = self._connection._receive_event_for_stream(self._config.stream_id)  # pyright: ignore[reportPrivateUsage]
        if event is None:
            return None
        self._last_message = event
        if event.error_code is not None:
            message = event.error_message or "Realtime Text-to-Speech stream failed"
            self._connection._deactivate_stream(self._config.stream_id)  # pyright: ignore[reportPrivateUsage]
            raise SonioxRealtimeError(f"{message} (code {event.error_code})")
        if event.terminated:
            self._connection._deactivate_stream(self._config.stream_id)  # pyright: ignore[reportPrivateUsage]
        return event

    def receive_events(self) -> Iterator[RealtimeTTSEvent]:
        """Yield events for this stream until it ends."""
        while True:
            event = self.receive_event()
            if event is None:
                break
            yield event
            if event.terminated:
                break

    def receive_audio_chunks(self) -> Iterator[bytes]:
        """Yield decoded audio chunks for this stream."""
        for event in self.receive_events():
            try:
                chunk = event.audio_bytes()
            except ValueError as exc:
                raise SonioxRealtimeError("Invalid realtime Text-to-Speech audio payload") from exc
            if chunk is not None:
                yield chunk
            if event.terminated:
                break
