from __future__ import annotations

from typing import TYPE_CHECKING

from ..types import CreateTemporaryApiKeyPayload
from ..types.realtime import RealtimeEvent, RealtimeSttConfig, RealtimeToken
from .async_stt import (
    AsyncRealtimeSTTClient,
    AsyncRealtimeSTTSession,
)
from .stt import RealtimeSTTClient, RealtimeSTTSession

if TYPE_CHECKING:
    from ..client import AsyncSonioxClient, SonioxClient

__all__ = [
    "RealtimeAPI",
    "RealtimeEvent",
    "RealtimeSTTClient",
    "RealtimeSTTSession",
    "RealtimeSttConfig",
    "RealtimeToken",
    "AsyncRealtimeAPI",
    "AsyncRealtimeSTTClient",
    "AsyncRealtimeSTTSession",
]


class AsyncRealtimeAPI:
    def __init__(self, client: AsyncSonioxClient) -> None:
        self._client = client
        self._stt = AsyncRealtimeSTTClient(client)

    @property
    def stt(self) -> AsyncRealtimeSTTClient:
        return self._stt

    async def get_temporary_api_key(self, payload: CreateTemporaryApiKeyPayload):
        return await self._client.auth.create_temporary_api_key(payload)


class RealtimeAPI:
    def __init__(self, client: SonioxClient) -> None:
        self._client = client
        self._stt = RealtimeSTTClient(client)

    @property
    def stt(self) -> RealtimeSTTClient:
        return self._stt

    def get_temporary_api_key(self, payload: CreateTemporaryApiKeyPayload):
        return self._client.auth.create_temporary_api_key(payload)
