from __future__ import annotations

from typing import TYPE_CHECKING

from ..types import GetConcurrencyLimitsResponse
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
