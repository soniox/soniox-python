from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, BinaryIO

from ..types import (
    File,
    GetFilesPayload,
    GetFilesResponse,
    UploadFilePayload,
)
from ._helpers import parse_response
from ._utils import normalize_file

if TYPE_CHECKING:
    from ..client import SonioxClient


class FilesAPI:
    """Synchronous wrappers around `/v1/files` routes."""

    def __init__(self, client: SonioxClient) -> None:
        self._client = client

    def list_files(self, limit: int = 1000, cursor: str | None = None) -> GetFilesResponse:
        payload = GetFilesPayload(limit=limit, cursor=cursor)
        params = payload.model_dump(exclude_none=True)
        response = self._client.request("GET", "/files", params=params)
        return parse_response(response, GetFilesResponse)

    def get_file(self, file_id: str) -> File:
        response = self._client.request("GET", f"/files/{file_id}")
        return parse_response(response, File)

    def delete_file(self, file_id: str) -> None:
        response = self._client.request("DELETE", f"/files/{file_id}")
        response.raise_for_status()

    def upload_file(
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
