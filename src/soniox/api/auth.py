from __future__ import annotations

from typing import TYPE_CHECKING

from ..types import (
    CreateTemporaryApiKeyPayload,
    CreateTemporaryApiKeyResponse,
    TemporaryApiKeyUsageType,
)
from ._utils import parse_response

if TYPE_CHECKING:
    from ..client import SonioxClient


class AuthAPI:
    def __init__(self, client: SonioxClient) -> None:
        self._client = client

    def create_temporary_api_key(
        self,
        *,
        usage_type: TemporaryApiKeyUsageType = "transcribe_websocket",
        expires_in_seconds: int = 5 * 60,
        client_reference_id: str | None = None,
        single_use: bool | None = None,
        max_session_duration_seconds: int | None = None,
    ) -> CreateTemporaryApiKeyResponse:
        """
        Create a temporary API key.

        Performs a POST request to ``/auth/temporary-api-key``.

        Raises:
            SonioxAPIError: When the API returns an error.
        """
        payload = CreateTemporaryApiKeyPayload(
            usage_type=usage_type,
            expires_in_seconds=expires_in_seconds,
            client_reference_id=client_reference_id,
            single_use=single_use,
            max_session_duration_seconds=max_session_duration_seconds,
        )
        response = self._client.request(
            "POST", "/auth/temporary-api-key", json=payload.model_dump(exclude_none=True)
        )
        return parse_response(response, CreateTemporaryApiKeyResponse)
