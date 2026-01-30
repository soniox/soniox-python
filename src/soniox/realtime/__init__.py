from __future__ import annotations

from functools import cached_property
from typing import TYPE_CHECKING

from ..types.realtime import RealtimeEvent, RealtimeSttConfig
from .stt import RealtimeSTTClient, RealtimeSTTSession

if TYPE_CHECKING:
    from ..client import AsyncSonioxClient, SonioxClient
    from .async_stt import (
        AsyncRealtimeSTTClient,
        AsyncRealtimeSTTSession,
    )
    from .stt import RealtimeSTTClient, RealtimeSTTSession
    from .stt_base import BaseRealtimeSTTSession

__all__ = [
    "RealtimeAPI",
    "RealtimeEvent",
    "RealtimeSTTClient",
    "RealtimeSTTSession",
    "RealtimeSttConfig",
    "AsyncRealtimeAPI",
    "AsyncRealtimeSTTClient",
    "AsyncRealtimeSTTSession",
    "BaseRealtimeSTTSession",
]


class AsyncRealtimeAPI:
    def __init__(self, client: AsyncSonioxClient) -> None:
        self._client = client

    @cached_property
    def stt(self) -> AsyncRealtimeSTTClient:
        from .async_stt import AsyncRealtimeSTTClient

        self._stt = AsyncRealtimeSTTClient(self._client)
        return self._stt


class RealtimeAPI:
    def __init__(self, client: SonioxClient) -> None:
        self._client = client

    @cached_property
    def stt(self) -> RealtimeSTTClient:
        from .stt import RealtimeSTTClient

        self._stt = RealtimeSTTClient(self._client)
        return self._stt
