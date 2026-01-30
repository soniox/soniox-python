from __future__ import annotations

import io
from pathlib import Path
from typing import BinaryIO, TypeVar

import httpx
from pydantic import BaseModel

from ..errors import SonioxAPIError
from ..types import (
    CreateTranscriptionConfig,
    CreateTranscriptionPayload,
)

ModelT = TypeVar("ModelT", bound=BaseModel)


def ensure_success(response: httpx.Response) -> None:
    if response.is_error:
        raise SonioxAPIError.from_response(response)


def parse_response(response: httpx.Response, model: type[ModelT]) -> ModelT:
    ensure_success(response)
    payload = response.json()
    return model.model_validate(payload)


async def parse_async_response(response: httpx.Response, model: type[ModelT]) -> ModelT:
    ensure_success(response)
    payload = response.json()
    return model.model_validate(payload)


def normalize_file(
    file: BinaryIO | bytes | Path | str,
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

    if isinstance(file, str):
        return normalize_file(Path(file), filename=filename)

    if isinstance(file, io.IOBase):
        effective_name = filename or getattr(file, "name", "upload.bin")
        return file, effective_name, False

    raise TypeError("file must be bytes, Path, or file-like stream.")


def build_create_payload(
    *,
    model: str,
    file_id: str | None,
    audio_url: str | None,
    client_reference_id: str | None,
    config: CreateTranscriptionConfig | None,
) -> CreateTranscriptionPayload:
    config_data = config.model_dump(exclude_none=True) if config else {}
    model_override = config_data.pop("model", None)
    client_ref_override = config_data.pop("client_reference_id", None)
    payload_model = model_override if model_override is not None else model
    payload_client_reference_id = (
        client_reference_id if client_reference_id is not None else client_ref_override
    )
    payload_data: dict[str, object | None] = {
        "model": payload_model,
        "file_id": file_id,
        "audio_url": audio_url,
        "client_reference_id": payload_client_reference_id,
    }
    payload_data.update(config_data)
    return CreateTranscriptionPayload.model_validate(payload_data)
