from __future__ import annotations

import json
from collections.abc import AsyncIterator, Mapping
from typing import TYPE_CHECKING, Any

from websockets import connect as async_ws_connect
from websockets.exceptions import ConnectionClosed

from ..errors import SonioxRealtimeError, SonioxValidationError
from ..types.realtime import RealtimeEvent, RealtimeSttConfig

if TYPE_CHECKING:
    from ..client import AsyncSonioxClient


class AsyncRealtimeSTTSession:
    def __init__(self, url: str, payload: Mapping[str, Any]) -> None:
        self._url = url
        self._payload = payload
        self._ws = None

    async def __aenter__(self) -> AsyncRealtimeSTTSession:
        self._ws = await async_ws_connect(self._url)
        await self._ws.send(json.dumps(self._payload))
        return self

    async def __aexit__(self) -> None:
        await self.close()

    async def close(self) -> None:
        if not self._ws:
            return
        try:
            await self._ws.send(b"")
        except ConnectionClosed:
            pass
        finally:
            await self._ws.close()
            self._ws = None

    async def send_audio_chunk(self, chunk: bytes) -> None:
        if not self._ws:
            raise SonioxRealtimeError("Realtime session is not connected")
        await self._ws.send(chunk)

    async def receive_event(self) -> RealtimeEvent | None:
        if not self._ws:
            raise SonioxRealtimeError("Realtime session is not connected")
        try:
            raw = await self._ws.recv()
        except ConnectionClosed:
            return None
        return RealtimeEvent.validate_event(raw)

    async def receive_events(self) -> AsyncIterator[RealtimeEvent]:
        while True:
            event = await self.receive_event()
            if event is None:
                break
            yield event
            if event.finished or event.error_code:
                break


class AsyncRealtimeSTTClient:
    def __init__(self, client: AsyncSonioxClient) -> None:
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
    ) -> AsyncRealtimeSTTSession:
        if config is None:
            if model is None:
                raise SonioxValidationError("`model` must be provided when config is not supplied")
            config = RealtimeSttConfig(model=model, audio_format=audio_format, **config_kwargs)

        payload = config.build_payload(self._resolve_key(api_key, temporary_api_key))
        return AsyncRealtimeSTTSession(self._client.websocket_base_url, payload)
