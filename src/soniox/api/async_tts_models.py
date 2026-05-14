from __future__ import annotations

from typing import TYPE_CHECKING

from ..types import GetTtsModelsResponse
from ._utils import parse_async_response

if TYPE_CHECKING:
    from ..client import AsyncSonioxClient


class AsyncTtsModelsAPI:
    def __init__(self, client: AsyncSonioxClient) -> None:
        self._client = client

    async def list(self) -> GetTtsModelsResponse:
        """
        List available Text-to-Speech models.

        Performs a GET request to ``/tts-models``.

        Raises:
            SonioxAPIError: When the API returns an error.
        """
        response = await self._client.request("GET", "/tts-models")
        return await parse_async_response(response, GetTtsModelsResponse)
