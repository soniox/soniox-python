from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, BinaryIO

from ..errors import SonioxNotFoundError
from ..types import (
    File,
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
        limit: int = 1000,
        cursor: str | None = None,
    ) -> GetFilesResponse:
        payload = GetFilesPayload(limit=limit, cursor=cursor)
        params = payload.model_dump(exclude_none=True)
        response = await self._client.request("GET", "/files", params=params)
        return await parse_async_response(response, GetFilesResponse)

    async def get(self, file_id: str) -> File:
        response = await self._client.request("GET", f"/files/{file_id}")
        return await parse_async_response(response, File)

    async def get_or_none(self, file_id: str) -> File | None:
        try:
            return await self.get(file_id)
        except SonioxNotFoundError:
            return None

    async def delete(self, file_id: str) -> None:
        response = await self._client.request("DELETE", f"/files/{file_id}")
        ensure_success(response)

    async def delete_if_exists(self, file_id: str) -> None:
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

    async def delete_all(self, *, limit: int = 1000) -> None:
        cursor: str | None = None
        while True:
            page = await self.list(limit=limit, cursor=cursor)
            for file in page.files:
                await self.delete(file.id)
            if not page.next_page_cursor:
                break
            cursor = page.next_page_cursor
