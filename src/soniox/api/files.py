from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, BinaryIO

from ..types import (
    File,
    GetFilesPayload,
    GetFilesResponse,
    UploadFilePayload,
)
from ._utils import ensure_success, normalize_file, parse_response

if TYPE_CHECKING:
    from ..client import SonioxClient


class FilesAPI:
    def __init__(self, client: SonioxClient) -> None:
        self._client = client

    def list(self, limit: int = 1000, cursor: str | None = None) -> GetFilesResponse:
        payload = GetFilesPayload(limit=limit, cursor=cursor)
        params = payload.model_dump(exclude_none=True)
        response = self._client.request("GET", "/files", params=params)
        return parse_response(response, GetFilesResponse)

    def get(self, file_id: str) -> File:
        response = self._client.request("GET", f"/files/{file_id}")
        return parse_response(response, File)

    def delete(self, file_id: str) -> None:
        response = self._client.request("DELETE", f"/files/{file_id}")
        ensure_success(response)

    def upload(
        self,
        file: BinaryIO | bytes | Path,
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
            response = self._client.request(
                "POST",
                "/files",
                data=data,
                files={"file": (effective_filename, file_obj)},
            )
            return parse_response(response, File)
        finally:
            if close_after:
                file_obj.close()

    def delete_all(self, *, limit: int = 1000) -> None:
        cursor: str | None = None
        while True:
            page = self.list(limit=limit, cursor=cursor)
            for file in page.files:
                self.delete(file.id)
            if not page.next_page_cursor:
                break
            cursor = page.next_page_cursor
