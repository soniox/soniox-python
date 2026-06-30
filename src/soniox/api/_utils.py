from __future__ import annotations

import io
import warnings
from pathlib import Path
from typing import BinaryIO, TypeVar

import httpx
from pydantic import BaseModel

from ..errors import SonioxAPIError, SonioxValidationError
from ..types import (
    CreateTranscriptionConfig,
    CreateTranscriptionPayload,
    CreateTtsConfig,
    CreateTtsPayload,
    LanguageCode,
    TranslationConfig,
)

ModelT = TypeVar("ModelT", bound=BaseModel)


def _warn_deprecated_config_fields(
    config: BaseModel | None, names: tuple[str, ...], advice: str
) -> None:
    """Emit a DeprecationWarning if any of ``names`` was explicitly set on ``config``.

    Read via ``model_fields_set`` (not attribute access) so it never fires for
    unset fields and never double-warns with pydantic's own ``deprecated=`` hook.
    """
    if config is None:
        return
    used = [n for n in names if n in config.model_fields_set]
    if used:
        warnings.warn(
            f"Setting {', '.join(used)} on {type(config).__name__} is deprecated; "
            f"{advice}. This will be removed in the next major release.",
            DeprecationWarning,
            stacklevel=3,
        )


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
    _warn_deprecated_config_fields(
        config,
        ("model", "client_reference_id"),
        "pass it directly to the create call instead",
    )
    config_data = config.model_dump(exclude_none=True) if config else {}
    model_override = config_data.pop("model", None)
    client_ref_override = config_data.pop("client_reference_id", None)
    return CreateTranscriptionPayload.model_validate(
        {
            "model": model_override if model_override is not None else model,
            "file_id": file_id,
            "audio_url": audio_url,
            "client_reference_id": (
                client_ref_override if client_ref_override is not None else client_reference_id
            ),
            **config_data,
        }
    )


def build_tts_payload(
    *,
    text: str,
    voice: str,
    model: str,
    config: CreateTtsConfig | None,
    language: str | None = None,
    audio_format: str | None = None,
    sample_rate: int | None = None,
    bitrate: int | None = None,
) -> CreateTtsPayload:
    # Deprecation shim — remove at the next major: make `language` required (drop its default
    # and the omit-language warning), delete the flat audio_format/sample_rate/bitrate kwargs and
    # their warning block, and drop model/voice/language from CreateTtsConfig along with the
    # _warn_deprecated_config_fields call and the override dance. The body then collapses to:
    # model_dump -> defaults -> model_validate. Keep _warn_deprecated_config_fields and the
    # `warnings` import until STT's shim is removed too.
    """Assemble a TTS payload from flat identity args (``text``/``voice``/``model``/
    ``language``) plus a ``config`` settings bag (``audio_format``/``sample_rate``/``bitrate``).

    Deprecated, kept one release: the flat ``audio_format``/``sample_rate``/``bitrate`` kwargs
    (move them to ``config``); ``model``/``voice``/``language`` set on ``config`` (pass them
    flat); and omitting ``language`` — it will be required in the next major release.
    """
    deprecated_flat = {
        k: v
        for k, v in {
            "audio_format": audio_format,
            "sample_rate": sample_rate,
            "bitrate": bitrate,
        }.items()
        if v is not None
    }
    if deprecated_flat:
        warnings.warn(
            f"Passing {', '.join(deprecated_flat)} directly to generate()/generate_to_file() "
            "is deprecated; set them on CreateTtsConfig instead. This will be removed in the "
            "next major release.",
            DeprecationWarning,
            stacklevel=3,
        )

    _warn_deprecated_config_fields(
        config,
        ("model", "voice", "language"),
        "pass it directly to generate()/generate_to_file() instead",
    )
    config_data = config.model_dump(exclude_none=True) if config else {}
    settings = {**deprecated_flat, **config_data}  # config wins for output settings
    # settings never holds None (exclude_none + deprecated_flat filter), so absent-key is
    # the only fallback case: get(key, default) and is-None, never falsy `or`.
    voice_override = settings.pop("voice", None)
    model_override = settings.pop("model", None)
    config_language = settings.pop("language", None)

    # language is identity, not a setting: the flat arg is the blessed path and wins; a
    # config value is honored (deprecated) next; relying on the "en" default is deprecated.
    if language is not None:
        resolved_language = language
    elif config_language is not None:
        resolved_language = config_language
    else:
        warnings.warn(
            "Relying on the default Text-to-Speech language 'en' is deprecated; pass "
            "language= explicitly. It will be required in the next major release.",
            DeprecationWarning,
            stacklevel=3,
        )
        resolved_language = "en"

    return CreateTtsPayload.model_validate(
        {
            "text": text,
            "voice": voice if voice_override is None else voice_override,
            "model": model if model_override is None else model_override,
            "language": resolved_language,
            "audio_format": settings.get("audio_format", "wav"),
            "sample_rate": settings.get("sample_rate"),
            "bitrate": settings.get("bitrate"),
            "speed": settings.get("speed"),
        }
    )


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
