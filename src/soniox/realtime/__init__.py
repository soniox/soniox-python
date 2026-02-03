from __future__ import annotations

from functools import cached_property
from typing import TYPE_CHECKING

from ..types.realtime import RealtimeEvent, RealtimeSTTConfig
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
    "RealtimeSTTConfig",
    "AsyncRealtimeAPI",
    "AsyncRealtimeSTTClient",
    "AsyncRealtimeSTTSession",
]


class AsyncRealtimeAPI:
    """Entrypoint for async realtime helpers on AsyncSonioxClient."""

    def __init__(self, client: AsyncSonioxClient) -> None:
        self._client = client

    @cached_property
    def stt(self) -> AsyncRealtimeSTTClient:
        from .async_stt import AsyncRealtimeSTTClient

        return AsyncRealtimeSTTClient(self._client)


class RealtimeAPI:
    """Entrypoint for realtime helpers on SonioxClient."""

    def __init__(self, client: SonioxClient) -> None:
        self._client = client

    @cached_property
    def stt(self) -> RealtimeSTTClient:
        from .stt import RealtimeSTTClient

        return RealtimeSTTClient(self._client)
