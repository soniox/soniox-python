from __future__ import annotations

from collections.abc import Generator
from typing import TYPE_CHECKING

from ..types import (
    GetUsageLogsPayload,
    GetUsageLogsResponse,
    UsageLogEntry,
    UsageLogsSort,
)
from ._utils import parse_response

if TYPE_CHECKING:
    from ..client import SonioxClient


class UsageLogsAPI:
    def __init__(self, client: SonioxClient) -> None:
        self._client = client

    def list(
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
        response = self._client.request("GET", "/usage-logs", params=params)
        return parse_response(response, GetUsageLogsResponse)

    def list_all(
        self,
        start_time: str,
        end_time: str,
        limit: int = 1000,
        sort: UsageLogsSort = "end_time_asc",
    ) -> Generator[UsageLogEntry, None, None]:
        """Iterate through all usage-log entries across all pages."""
        cursor = None
        while True:
            response = self.list(
                start_time=start_time,
                end_time=end_time,
                limit=limit,
                sort=sort,
                cursor=cursor,
            )
            yield from response.usage_logs
            cursor = response.next_page_cursor
            if not cursor:
                break
