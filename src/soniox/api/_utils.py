from __future__ import annotations

import io
from pathlib import Path
from typing import BinaryIO, TypeVar

import httpx
from pydantic import BaseModel

from ..errors import SonioxAPIError, SonioxValidationError
from ..types import (
    CreateTranscriptionConfig,
    CreateTranscriptionPayload,
    LanguageCode,
    TranslationConfig,
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


def build_translate_config(
    *,
    to: LanguageCode | None,
    source: LanguageCode | None,
    between: tuple[LanguageCode, LanguageCode] | None,
    config: CreateTranscriptionConfig | None,
) -> CreateTranscriptionConfig:
    """Return a config with translation and language fields populated from the kwargs.

    Requires exactly one of ``to`` or ``between``. ``source`` is only valid with ``to``
    and is passed as a strict language hint. Forces ``enable_language_identification=True``.
    Other config fields are preserved.
    """
    if (to is None) == (between is None):
        raise SonioxValidationError("Provide exactly one of `to` or `between`")
    if source is not None and to is None:
        raise SonioxValidationError("`source` is only valid with `to`")

    base = config.model_copy() if config else CreateTranscriptionConfig()
    if to is not None:
        base.translation = TranslationConfig(type="one_way", target_language=to)
        if source:
            base.language_hints = [source]
            base.language_hints_strict = True
    else:
        assert between is not None  # validated above
        a, b = between
        base.translation = TranslationConfig(type="two_way", language_a=a, language_b=b)

    base.enable_language_identification = True
    return base
