from __future__ import annotations

import json
from collections.abc import Iterator, Mapping
from typing import TYPE_CHECKING, Any

from websockets.exceptions import ConnectionClosed
from websockets.sync.client import connect as sync_ws_connect

from ..errors import SonioxRealtimeError, SonioxValidationError
from ..types.realtime import RealtimeEvent, RealtimeSttConfig

if TYPE_CHECKING:
    from ..client import SonioxClient


class RealtimeSTTSession:
    def __init__(self, url: str, payload: Mapping[str, Any]) -> None:
        self._url = url
        self._payload = payload
        self._ws = None

    def __enter__(self) -> RealtimeSTTSession:
        self._ws = sync_ws_connect(self._url)
        self._ws.send(json.dumps(self._payload))
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

    def send_audio_chunk(self, chunk: bytes) -> None:
        if not self._ws:
            raise SonioxRealtimeError("Realtime session is not connected")
        self._ws.send(chunk)

    def receive_event(self) -> RealtimeEvent | None:
        if not self._ws:
            raise SonioxRealtimeError("Realtime session is not connected")
        try:
            raw = self._ws.recv()
        except ConnectionClosed:
            return None
        return RealtimeEvent.validate_event(raw)

    def receive_events(self) -> Iterator[RealtimeEvent]:
        while True:
            event = self.receive_event()
            if event is None:
                break
            yield event
            if event.finished or event.error_code:
                break


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
