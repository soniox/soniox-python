from __future__ import annotations

from collections.abc import AsyncGenerator
from pathlib import Path
from typing import TYPE_CHECKING, BinaryIO

from ..errors import SonioxNotFoundError
from ..types import (
    File,
    GetFilesCountResponse,
    GetFilesPayload,
    GetFilesResponse,
    UploadFilePayload,
)
from ._utils import ensure_success, normalize_file, parse_async_response

if TYPE_CHECKING:
    from ..client import AsyncSonioxClient


class AsyncFilesAPI:
    def __init__(self, client: AsyncSonioxClient) -> None:
        self._client = client

    async def list(
        self,
        limit: int = 100,
        cursor: str | None = None,
    ) -> GetFilesResponse:
        """
        List uploaded files.

        Performs a GET request to ``/files`` with optional pagination.

        Raises:
            SonioxAPIError: When the API returns an error.
        """
        payload = GetFilesPayload(limit=limit, cursor=cursor)
        params = payload.model_dump(exclude_none=True)
        response = await self._client.request("GET", "/files", params=params)
        return await parse_async_response(response, GetFilesResponse)

    async def count(self) -> GetFilesCountResponse:
        """
        Return a breakdown of uploaded file counts.

        Performs a GET request to ``/files/count``.

        Raises:
            SonioxAPIError: When the API returns an error.
        """
        response = await self._client.request("GET", "/files/count")
        return await parse_async_response(response, GetFilesCountResponse)

    async def list_all(self, limit: int = 100) -> AsyncGenerator[File, None]:
        """
        Iterate through all uploaded files across all pages.

        Yields:
            File: The next file object from the API.

        Raises:
            SonioxAPIError: When the API returns an error.
        """
        cursor: str | None = None

        while True:
            response = await self.list(limit=limit, cursor=cursor)

            for file in response.files:
                yield file

            cursor = response.next_page_cursor
            if not cursor:
                break

    async def get(self, file_id: str) -> File:
        """
        Retrieve a file by ID.

        Performs a GET request to ``/files/{file_id}``.

        Raises:
            SonioxAPIError: When the API returns an error.
        """
        response = await self._client.request("GET", f"/files/{file_id}")
        return await parse_async_response(response, File)

    async def get_or_none(self, file_id: str) -> File | None:
        """
        Retrieve a file by ID.

        Returns ``None`` if the file does not exist.

        Raises:
            SonioxAPIError: When the API returns an error.
        """
        try:
            return await self.get(file_id)
        except SonioxNotFoundError:
            return None

    async def delete(self, file_id: str) -> None:
        """
        Delete a file by ID.

        Performs a DELETE request to ``/files/{file_id}``.

        Raises:
            SonioxAPIError: When the API returns an error.
        """
        response = await self._client.request("DELETE", f"/files/{file_id}")
        ensure_success(response)

    async def delete_if_exists(self, file_id: str) -> None:
        """
        Delete a file by ID if it exists.

        Ignores missing files.

        Raises:
            SonioxAPIError: When the API returns an error.
        """
        try:
            await self.delete(file_id)
        except SonioxNotFoundError:
            return

    async def upload(
        self,
        file: BinaryIO | bytes | Path | str,
        *,
        filename: str | None = None,
        client_reference_id: str | None = None,
    ) -> File:
        """
        Upload a file.

        Performs a multipart POST request to ``/files``.

        Raises:
            SonioxAPIError: When the API returns an error.
        """
        file_obj, effective_filename, close_after = normalize_file(file, filename=filename)
        payload = UploadFilePayload(client_reference_id=client_reference_id)
        data = payload.model_dump(exclude_none=True)
        if not data:
            data = None

        try:
            response = await self._client.request(
                "POST",
                "/files",
                data=data,
                files={"file": (effective_filename, file_obj)},
            )
            return await parse_async_response(response, File)
        finally:
            if close_after:
                file_obj.close()

    async def delete_all(self, limit: int = 100) -> None:
        """
        Delete all files.

        Iterates through all pages and deletes each file. Stops and raises on the first failed deletion.

        Raises:
            SonioxAPIError: When the API returns an error.
        """
        async for file in self.list_all(limit=limit):
            await self.delete_if_exists(file.id)
