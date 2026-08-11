from __future__ import annotations

from typing import TYPE_CHECKING

from ..types import (
    ConcurrentStreamKind,
    ConcurrentStreamsPeriodSec,
    GetConcurrencyLimitsResponse,
    GetConcurrentStreamsHistoryPayload,
    GetConcurrentStreamsHistoryResponse,
)
from ._utils import parse_async_response

if TYPE_CHECKING:
    from ..client import AsyncSonioxClient


class AsyncConcurrencyLimitsAPI:
    def __init__(self, client: AsyncSonioxClient) -> None:
        self._client = client

    async def get(self) -> GetConcurrencyLimitsResponse:
        """
        Get current concurrent sessions and configured limits.

        Performs a GET request to ``/concurrency-limits``.

        Returns:
            Project- and organization-scoped current counts and configured
            limits for realtime STT and TTS sessions.

        Raises:
            SonioxAPIError: When the API returns an error.
        """
        response = await self._client.request("GET", "/concurrency-limits")
        return await parse_async_response(response, GetConcurrencyLimitsResponse)

    async def history(
        self,
        start_time: str,
        end_time: str,
        *,
        period_sec: ConcurrentStreamsPeriodSec,
        kind: ConcurrentStreamKind,
    ) -> GetConcurrentStreamsHistoryResponse:
        """
        Get historical concurrent stream counts, aggregated per period.

        Performs a GET request to ``/concurrent-streams-history``.

        Args:
            start_time: Start of the window (inclusive), ISO 8601 UTC.
            end_time: End of the window (exclusive), ISO 8601 UTC, after ``start_time``.
            period_sec: Aggregation period: 60, 3600, or 86400. Also caps the window
                length the server accepts (7 days for 60).
            kind: ``stt`` for Speech-to-Text sessions, ``tts`` for Text-to-Speech.

        Raises:
            SonioxAPIError: When the API returns an error.
        """
        payload = GetConcurrentStreamsHistoryPayload(
            start_time=start_time,
            end_time=end_time,
            period_sec=period_sec,
            kind=kind,
        )
        response = await self._client.request(
            "GET", "/concurrent-streams-history", params=payload.model_dump()
        )
        return await parse_async_response(response, GetConcurrentStreamsHistoryResponse)
