from __future__ import annotations

from typing import TYPE_CHECKING

from ..types import GetTtsModelsResponse
from ._utils import parse_response

if TYPE_CHECKING:
    from ..client import SonioxClient


class TtsModelsAPI:
    def __init__(self, client: SonioxClient) -> None:
        self._client = client

    def list(self) -> GetTtsModelsResponse:
        """
        List available Text-to-Speech models.

        Performs a GET request to ``/tts-models``.

        Raises:
            SonioxAPIError: When the API returns an error.
        """
        response = self._client.request("GET", "/tts-models")
        return parse_response(response, GetTtsModelsResponse)
