from __future__ import annotations

from collections.abc import AsyncGenerator
from pathlib import Path
from typing import TYPE_CHECKING, BinaryIO

from ..errors import SonioxNotFoundError
from ..types import (
    GetVoicesCountResponse,
    GetVoicesPayload,
    GetVoicesResponse,
    RecomputeVoicePayload,
    Voice,
)
from ._utils import ensure_success, normalize_file, parse_async_response

if TYPE_CHECKING:
    from ..client import AsyncSonioxClient


class AsyncVoicesAPI:
    def __init__(self, client: AsyncSonioxClient) -> None:
        self._client = client

    async def list(self, limit: int = 100, cursor: str | None = None) -> GetVoicesResponse:
        """
        List voices in the project.

        Performs a GET request to ``/voices`` with optional pagination.

        Raises:
            SonioxAPIError: When the API returns an error.
        """
        payload = GetVoicesPayload(limit=limit, cursor=cursor)
        params = payload.model_dump(exclude_none=True)
        response = await self._client.request("GET", "/voices", params=params)
        return await parse_async_response(response, GetVoicesResponse)

    async def count(self) -> GetVoicesCountResponse:
        """
        Return the total number of voices in the project.

        Performs a GET request to ``/voices/count``.

        Raises:
            SonioxAPIError: When the API returns an error.
        """
        response = await self._client.request("GET", "/voices/count")
        return await parse_async_response(response, GetVoicesCountResponse)

    async def list_all(self, limit: int = 100) -> AsyncGenerator[Voice, None]:
        """
        Iterate through all voices across all pages.

        Yields:
            Voice: The next voice object from the API.

        Raises:
            SonioxAPIError: When the API returns an error.
        """
        cursor: str | None = None

        while True:
            response = await self.list(limit=limit, cursor=cursor)

            for voice in response.voices:
                yield voice

            cursor = response.next_page_cursor
            if not cursor:
                break

    async def get(self, voice_id: str) -> Voice:
        """
        Retrieve a voice by ID.

        Performs a GET request to ``/voices/{voice_id}``.

        Raises:
            SonioxAPIError: When the API returns an error.
        """
        response = await self._client.request("GET", f"/voices/{voice_id}")
        return await parse_async_response(response, Voice)

    async def get_or_none(self, voice_id: str) -> Voice | None:
        """
        Retrieve a voice by ID.

        Returns ``None`` if the voice does not exist.

        Raises:
            SonioxAPIError: When the API returns an error.
        """
        try:
            return await self.get(voice_id)
        except SonioxNotFoundError:
            return None

    async def create(
        self,
        file: BinaryIO | bytes | Path | str,
        *,
        name: str,
        filename: str | None = None,
    ) -> Voice:
        """
        Create a cloned voice from a reference audio clip.

        Performs a multipart POST request to ``/voices``.

        Raises:
            SonioxAPIError: When the API returns an error.
        """
        file_obj, effective_filename, close_after = normalize_file(file, filename=filename)
        try:
            response = await self._client.request(
                "POST",
                "/voices",
                data={"name": name},
                files={"file": (effective_filename, file_obj)},
            )
            return await parse_async_response(response, Voice)
        finally:
            if close_after:
                file_obj.close()

    async def recompute(self, voice_id: str, *, model: str | None = None) -> Voice:
        """
        Prepare an existing voice for models it is not ready for yet.

        Performs a POST request to ``/voices/{voice_id}/recompute``. When ``model``
        is omitted, the voice is prepared for every available model it is not ready
        for; models it is already prepared for are left unchanged.

        Raises:
            SonioxAPIError: When the API returns an error.
        """
        payload = RecomputeVoicePayload(model=model)
        response = await self._client.request(
            "POST",
            f"/voices/{voice_id}/recompute",
            json=payload.model_dump(exclude_none=True),
        )
        return await parse_async_response(response, Voice)

    async def delete(self, voice_id: str) -> None:
        """
        Delete a voice by ID.

        Performs a DELETE request to ``/voices/{voice_id}``.

        Raises:
            SonioxAPIError: When the API returns an error.
        """
        response = await self._client.request("DELETE", f"/voices/{voice_id}")
        ensure_success(response)

    async def delete_if_exists(self, voice_id: str) -> None:
        """
        Delete a voice by ID if it exists.

        Ignores missing voices.

        Raises:
            SonioxAPIError: When the API returns an error.
        """
        try:
            await self.delete(voice_id)
        except SonioxNotFoundError:
            return
