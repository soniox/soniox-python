from __future__ import annotations

from typing import TYPE_CHECKING

from ..types import CreateTemporaryApiKeyPayload, CreateTemporaryApiKeyResponse
from ._helpers import parse_async_response

if TYPE_CHECKING:
    from ..client import AsyncSonioxClient


class AsyncAuthAPI:
    def __init__(self, client: AsyncSonioxClient) -> None:
        self._client = client

    async def create_temporary_api_key(
        self, payload: CreateTemporaryApiKeyPayload
    ) -> CreateTemporaryApiKeyResponse:
        response = await self._client.request(
            "POST", "/auth/temporary-api-key", json=payload.model_dump(exclude_none=True)
        )
        return await parse_async_response(response, CreateTemporaryApiKeyResponse)
