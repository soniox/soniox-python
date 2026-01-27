from __future__ import annotations

from typing import TYPE_CHECKING

from ..types import CreateTemporaryApiKeyPayload, CreateTemporaryApiKeyResponse
from ._helpers import parse_response

if TYPE_CHECKING:
    from ..client import SonioxClient


class AuthAPI:
    def __init__(self, client: SonioxClient) -> None:
        self._client = client

    def create_temporary_api_key(
        self, payload: CreateTemporaryApiKeyPayload
    ) -> CreateTemporaryApiKeyResponse:
        response = self._client.request(
            "POST", "/auth/temporary-api-key", json=payload.model_dump(exclude_none=True)
        )
        return parse_response(response, CreateTemporaryApiKeyResponse)
