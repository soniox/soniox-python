from __future__ import annotations

from typing import TYPE_CHECKING

from ..types import GetModelsResponse
from ._helpers import parse_response

if TYPE_CHECKING:
    from ..client import SonioxClient


class ModelsAPI:
    def __init__(self, client: SonioxClient) -> None:
        self._client = client

    def list_models(self) -> GetModelsResponse:
        response = self._client.request("GET", "/models")
        return parse_response(response, GetModelsResponse)
