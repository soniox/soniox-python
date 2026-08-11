from __future__ import annotations

from typing import TYPE_CHECKING

from ..types import GetUsageSummaryPayload, GetUsageSummaryResponse
from ._utils import parse_async_response

if TYPE_CHECKING:
    from ..client import AsyncSonioxClient


class AsyncUsageAPI:
    def __init__(self, client: AsyncSonioxClient) -> None:
        self._client = client

    async def summary(self, start_time: str, end_time: str) -> GetUsageSummaryResponse:
        """
        Return daily cost and activity for the project, per model and in total.

        Performs a GET request to ``/usage/summary``.

        Args:
            start_time: Start of the window (inclusive), ISO 8601 UTC.
            end_time: End of the window (exclusive), ISO 8601 UTC. A UTC day is included
                when the window covers any part of it, so an ``end_time`` at exactly
                midnight leaves out its own day. At most 366 days.

        Raises:
            SonioxAPIError: When the API returns an error.
        """
        payload = GetUsageSummaryPayload(start_time=start_time, end_time=end_time)
        response = await self._client.request("GET", "/usage/summary", params=payload.model_dump())
        return await parse_async_response(response, GetUsageSummaryResponse)
