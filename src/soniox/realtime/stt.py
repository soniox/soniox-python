from __future__ import annotations

import json
from collections.abc import Callable, Iterator, Mapping
from typing import TYPE_CHECKING, Any

from websockets.exceptions import ConnectionClosed
from websockets.sync.client import connect as sync_ws_connect

from ..errors import SonioxRealtimeError, SonioxValidationError
from ..types.realtime import (
    RealtimeErrorCallback,
    RealtimeEvent,
    RealtimeEventCallback,
    RealtimeSessionCallback,
    RealtimeSessionEvent,
    RealtimeSttConfig,
)

if TYPE_CHECKING:
    from ..client import SonioxClient


class RealtimeSTTSession:
    def __init__(
        self,
        url: str,
        payload: Mapping[str, Any],
    ) -> None:
        self._url = url
        self._payload = payload
        self._ws = None
        self._listeners: dict[RealtimeSessionEvent, list[Callable[..., None]]] = {}

    def __enter__(self) -> RealtimeSTTSession:
        self._ws = sync_ws_connect(self._url)
        self._ws.send(json.dumps(self._payload))
        self._emit(RealtimeSessionEvent.OPEN)
        return self

    def __exit__(self) -> None:
        self.close()

    def close(self) -> None:
        if not self._ws:
            return
        try:
            self._ws.send(b"")
        except ConnectionClosed:
            pass
        finally:
            self._ws.close()
            self._ws = None
        self._emit(RealtimeSessionEvent.CLOSE)

    def send_audio_chunk(self, chunk: bytes) -> None:
        if not self._ws:
            raise SonioxRealtimeError("Realtime session is not connected")
        try:
            self._ws.send(chunk)
        except Exception as exc:
            self._emit_error(exc)
            raise

    def stream_audio(
        self,
        chunks: bytes | bytearray | memoryview | Iterator[bytes | bytearray | memoryview],
    ) -> None:
        if isinstance(chunks, bytes | bytearray | memoryview):
            self.send_audio_chunk(bytes(chunks))
            return

        for chunk in chunks:
            self.send_audio_chunk(bytes(chunk))

    def receive_event(self) -> RealtimeEvent | None:
        if not self._ws:
            raise SonioxRealtimeError("Realtime session is not connected")
        try:
            raw = self._ws.recv()
        except ConnectionClosed:
            return None
        event = RealtimeEvent.validate_event(raw)
        self._emit(RealtimeSessionEvent.MESSAGE, event)
        return event

    def receive_events(self) -> Iterator[RealtimeEvent]:
        while True:
            event = self.receive_event()
            if event is None:
                break
            yield event
            if event.finished or event.error_code:
                break

    def handle_events(self, handler: Callable[[RealtimeEvent], None]) -> None:
        for event in self.receive_events():
            handler(event)

    def on_event(self, event_type: RealtimeSessionEvent, callback: Callable[..., None]) -> None:
        self._listeners.setdefault(event_type, []).append(callback)

    def on_message(self, callback: RealtimeEventCallback) -> None:
        def _wrapper(event: RealtimeEvent, _: RealtimeSTTSession) -> None:
            callback(event)

        self.on_event(RealtimeSessionEvent.MESSAGE, _wrapper)

    def on_open(self, callback: RealtimeSessionCallback) -> None:
        def _wrapper(event_type: RealtimeSessionEvent, session: RealtimeSTTSession) -> None:
            callback(event_type, session)

        self.on_event(RealtimeSessionEvent.OPEN, _wrapper)

    def on_close(self, callback: RealtimeSessionCallback) -> None:
        def _wrapper(event_type: RealtimeSessionEvent, session: RealtimeSTTSession) -> None:
            callback(event_type, session)

        self.on_event(RealtimeSessionEvent.CLOSE, _wrapper)

    def on_error(self, callback: RealtimeErrorCallback) -> None:
        def _wrapper(exc: Exception, session: RealtimeSTTSession) -> None:
            callback(exc, session)

        self.on_event(RealtimeSessionEvent.ERROR, _wrapper)

    def _emit(self, event_type: RealtimeSessionEvent, payload: Any | None = None) -> None:
        for callback in self._listeners.get(event_type, []):
            try:
                if event_type is RealtimeSessionEvent.MESSAGE:
                    callback(payload, self)
                elif event_type is RealtimeSessionEvent.ERROR:
                    callback(payload, self)
                else:
                    callback(event_type, self)
            except Exception:
                pass

    def _emit_error(self, exc: Exception) -> None:
        self._emit(RealtimeSessionEvent.ERROR, exc)


class RealtimeSTTClient:
    def __init__(self, client: SonioxClient) -> None:
        self._client = client

    def _resolve_key(self, api_key: str | None, temporary_api_key: str | None) -> str:
        key = temporary_api_key or api_key or self._client.api_key
        if not key:
            raise SonioxValidationError("API key is required to start a realtime session")
        return key

    def connect(
        self,
        *,
        config: RealtimeSttConfig | None = None,
        model: str | None = None,
        audio_format: str = "auto",
        api_key: str | None = None,
        temporary_api_key: str | None = None,
        **config_kwargs: Any,
    ) -> RealtimeSTTSession:
        if config is None:
            if model is None:
                raise SonioxValidationError("`model` must be provided when config is not supplied")
            config = RealtimeSttConfig(model=model, audio_format=audio_format, **config_kwargs)

        payload = config.build_payload(self._resolve_key(api_key, temporary_api_key))
        return RealtimeSTTSession(self._client.websocket_base_url, payload)
