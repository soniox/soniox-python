from __future__ import annotations

from typing import TYPE_CHECKING

from ..types import GetModelsResponse
from ._utils import parse_async_response

if TYPE_CHECKING:
    from ..client import AsyncSonioxClient


class AsyncModelsAPI:
    def __init__(self, client: AsyncSonioxClient) -> None:
        self._client = client

    async def list(self) -> GetModelsResponse:
        """
        List available models.

        Performs a GET request to ``/models``.

        Raises:
            SonioxAPIError: When the API returns an error.
        """
        response = await self._client.request("GET", "/models")
        return await parse_async_response(response, GetModelsResponse)
