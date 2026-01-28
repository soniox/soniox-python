from __future__ import annotations

from functools import cached_property
from typing import TYPE_CHECKING

from ..types import CreateTemporaryApiKeyPayload
from ..types.realtime import RealtimeEvent, RealtimeSttConfig, RealtimeToken
from .stt import RealtimeSTTClient, RealtimeSTTSession

if TYPE_CHECKING:
    from ..client import AsyncSonioxClient, SonioxClient
    from .async_stt import (
        AsyncRealtimeSTTClient,
        AsyncRealtimeSTTSession,
    )
    from .stt import RealtimeSTTClient, RealtimeSTTSession

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

    @cached_property
    def stt(self) -> AsyncRealtimeSTTClient:
        from .async_stt import AsyncRealtimeSTTClient

        self._stt = AsyncRealtimeSTTClient(self._client)
        return self._stt

    async def get_temporary_api_key(self, payload: CreateTemporaryApiKeyPayload):
        return await self._client.auth.create_temporary_api_key(payload)


class RealtimeAPI:
    def __init__(self, client: SonioxClient) -> None:
        self._client = client

    @property
    def stt(self) -> RealtimeSTTClient:
        from .stt import RealtimeSTTClient

        self._stt = RealtimeSTTClient(self._client)
        return self._stt

    def get_temporary_api_key(self, payload: CreateTemporaryApiKeyPayload):
        return self._client.auth.create_temporary_api_key(payload)
