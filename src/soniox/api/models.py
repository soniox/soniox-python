from __future__ import annotations

from typing import TYPE_CHECKING

from ..types import GetModelsResponse
from ._utils import parse_response

if TYPE_CHECKING:
    from ..client import SonioxClient


class ModelsAPI:
    def __init__(self, client: SonioxClient) -> None:
        self._client = client

    def list(self) -> GetModelsResponse:
        """
        List available models.

        Performs a GET request to ``/models``.

        Raises:
            SonioxAPIError: When the API returns an error.
        """
        response = self._client.request("GET", "/models")
        return parse_response(response, GetModelsResponse)
