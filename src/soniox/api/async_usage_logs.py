from __future__ import annotations

from collections.abc import AsyncGenerator
from typing import TYPE_CHECKING

from ..types import (
    GetUsageLogsPayload,
    GetUsageLogsResponse,
    UsageLogEntry,
    UsageLogsSort,
)
from ._utils import parse_async_response

if TYPE_CHECKING:
    from ..client import AsyncSonioxClient


class AsyncUsageLogsAPI:
    def __init__(self, client: AsyncSonioxClient) -> None:
        self._client = client

    async def list(
        self,
        start_time: str,
        end_time: str,
        limit: int = 1000,
        sort: UsageLogsSort = "end_time_asc",
        cursor: str | None = None,
    ) -> GetUsageLogsResponse:
        """
        List usage-log entries for a time window.

        Performs a GET request to ``/usage-logs``.

        Args:
            start_time: Start of the window (inclusive). Filters by request end time.
            end_time: End of the window (exclusive). Filters by request end time.
            limit: Maximum number of entries to return (1–1000).
            sort: Sort order by end_time.
            cursor: Pagination cursor for the next page.

        Raises:
            SonioxAPIError: When the API returns an error.
        """
        payload = GetUsageLogsPayload(
            start_time=start_time,
            end_time=end_time,
            limit=limit,
            sort=sort,
            cursor=cursor,
        )
        params = payload.model_dump(exclude_none=True)
        response = await self._client.request("GET", "/usage-logs", params=params)
        return await parse_async_response(response, GetUsageLogsResponse)

    async def list_all(
        self,
        start_time: str,
        end_time: str,
        limit: int = 1000,
        sort: UsageLogsSort = "end_time_asc",
    ) -> AsyncGenerator[UsageLogEntry, None]:
        """Iterate through all usage-log entries across all pages."""
        cursor = None
        while True:
            response = await self.list(
                start_time=start_time,
                end_time=end_time,
                limit=limit,
                sort=sort,
                cursor=cursor,
            )
            for entry in response.usage_logs:
                yield entry
            cursor = response.next_page_cursor
            if not cursor:
                break
