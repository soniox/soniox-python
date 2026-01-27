from __future__ import annotations

import io
from pathlib import Path
from typing import BinaryIO, TypeVar

import httpx
from pydantic import BaseModel

from ..errors import ApiErrorException

ModelT = TypeVar("ModelT", bound=BaseModel)


def ensure_success(response: httpx.Response) -> None:
    if response.is_error:
        raise ApiErrorException.from_response(response)


def parse_response(response: httpx.Response, model: type[ModelT]) -> ModelT:
    ensure_success(response)
    payload = response.json()
    return model.model_validate(payload)


async def parse_async_response(response: httpx.Response, model: type[ModelT]) -> ModelT:
    ensure_success(response)
    payload = response.json()
    return model.model_validate(payload)


def normalize_file(
    file: BinaryIO | bytes | Path,
    filename: str | None = None,
) -> tuple[BinaryIO, str, bool]:
    """Return (file-like, filename, should_close) tuple for upload."""
    if isinstance(file, bytes | bytearray):
        file_obj = io.BytesIO(file)
        effective_name = filename or "upload.bin"
        return file_obj, effective_name, True

    if isinstance(file, Path):
        file_obj = file.open("rb")
        effective_name = filename or file.name
        return file_obj, effective_name, True

    if isinstance(file, io.IOBase):
        effective_name = filename or getattr(file, "name", "upload.bin")
        return file, effective_name, False

    raise TypeError("file must be bytes, Path, or file-like stream.")
