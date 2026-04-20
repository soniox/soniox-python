from __future__ import annotations

from functools import cached_property
from typing import TYPE_CHECKING

from ..types.realtime import RealtimeEvent, RealtimeSTTConfig, RealtimeTTSConfig, RealtimeTTSEvent
from .stt import RealtimeSTTClient, RealtimeSTTSession
from .tts import (
    RealtimeTTSClient,
    RealtimeTTSConnection,
    RealtimeTTSMultiplexedConnection,
    RealtimeTTSStream,
)

if TYPE_CHECKING:
    from ..client import AsyncSonioxClient, SonioxClient
    from .async_stt import (
        AsyncRealtimeSTTClient,
        AsyncRealtimeSTTSession,
    )
    from .async_tts import (
        AsyncRealtimeTTSClient,
        AsyncRealtimeTTSConnection,
        AsyncRealtimeTTSMultiplexedConnection,
        AsyncRealtimeTTSStream,
    )
    from .stt import RealtimeSTTClient, RealtimeSTTSession
    from .tts import (
        RealtimeTTSClient,
        RealtimeTTSConnection,
        RealtimeTTSMultiplexedConnection,
        RealtimeTTSStream,
    )

__all__ = [
    "RealtimeAPI",
    "RealtimeEvent",
    "RealtimeSTTClient",
    "RealtimeSTTSession",
    "RealtimeSTTConfig",
    "RealtimeTTSClient",
    "RealtimeTTSConnection",
    "RealtimeTTSMultiplexedConnection",
    "RealtimeTTSStream",
    "RealtimeTTSConfig",
    "RealtimeTTSEvent",
    "AsyncRealtimeAPI",
    "AsyncRealtimeSTTClient",
    "AsyncRealtimeSTTSession",
    "AsyncRealtimeTTSClient",
    "AsyncRealtimeTTSConnection",
    "AsyncRealtimeTTSMultiplexedConnection",
    "AsyncRealtimeTTSStream",
]


class AsyncRealtimeAPI:
    """Entrypoint for async realtime helpers on AsyncSonioxClient."""

    def __init__(self, client: AsyncSonioxClient) -> None:
        self._client = client

    @cached_property
    def stt(self) -> AsyncRealtimeSTTClient:
        from .async_stt import AsyncRealtimeSTTClient

        return AsyncRealtimeSTTClient(self._client)

    @cached_property
    def tts(self) -> AsyncRealtimeTTSClient:
        from .async_tts import AsyncRealtimeTTSClient

        return AsyncRealtimeTTSClient(self._client)


class RealtimeAPI:
    """Entrypoint for realtime helpers on SonioxClient."""

    def __init__(self, client: SonioxClient) -> None:
        self._client = client

    @cached_property
    def stt(self) -> RealtimeSTTClient:
        from .stt import RealtimeSTTClient

        return RealtimeSTTClient(self._client)

    @cached_property
    def tts(self) -> RealtimeTTSClient:
        from .tts import RealtimeTTSClient

        return RealtimeTTSClient(self._client)
