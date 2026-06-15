"""
Tests targeting the specific uncovered lines that don't fit naturally into
other test files: ``normalize_file`` input variants, the default branch in
``SonioxAPIError._map_status_to_exception``, and the pydantic validators on
``TranslationConfig`` and ``CreateTranscriptionPayload``.
"""

from __future__ import annotations

import io
from pathlib import Path

import pytest
import respx
from httpx import Response
from pydantic import ValidationError

from soniox.api._utils import normalize_file
from soniox.client import SonioxClient
from soniox.errors import SonioxAPIError
from soniox.types import TranslationConfig
from soniox.types.api import CreateTranscriptionPayload
from tests.helpers import BASE_URL


# ---------------------------------------------------------------------------
# normalize_file - covers every input branch
# ---------------------------------------------------------------------------


def test_normalize_file_from_bytes_returns_bytesio() -> None:
    obj, name, should_close = normalize_file(b"audio")
    assert obj.read() == b"audio"
    assert name == "upload.bin"
    assert should_close is True


def test_normalize_file_from_bytes_uses_given_filename() -> None:
    _, name, _ = normalize_file(b"audio", filename="clip.wav")
    assert name == "clip.wav"


def test_normalize_file_from_path(tmp_path: Path) -> None:
    audio = tmp_path / "clip.raw"
    audio.write_bytes(b"hi")
    obj, name, should_close = normalize_file(audio)
    try:
        assert obj.read() == b"hi"
        assert name == "clip.raw"
        assert should_close is True
    finally:
        obj.close()


def test_normalize_file_from_str_path(tmp_path: Path) -> None:
    audio = tmp_path / "clip.raw"
    audio.write_bytes(b"hi")
    obj, name, should_close = normalize_file(str(audio), filename="override.bin")
    try:
        assert obj.read() == b"hi"
        assert name == "override.bin"
        assert should_close is True
    finally:
        obj.close()


def test_normalize_file_from_stream_keeps_ownership() -> None:
    """A caller-provided stream must NOT be auto-closed by the SDK."""
    stream = io.BytesIO(b"audio")
    stream.name = "named.mp3"  # type: ignore[attr-defined]
    obj, name, should_close = normalize_file(stream)
    assert obj is stream
    assert name == "named.mp3"
    assert should_close is False


def test_normalize_file_rejects_unknown_type() -> None:
    with pytest.raises(TypeError):
        normalize_file(42)  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# SonioxAPIError._map_status_to_exception default branch
# ---------------------------------------------------------------------------


@respx.mock
def test_unknown_4xx_status_falls_back_to_generic_api_error(client: SonioxClient) -> None:
    """A status code outside the known map (e.g. 418) must not crash - it
    falls back to the base ``SonioxAPIError`` class."""
    respx.get(f"{BASE_URL}/files").mock(return_value=Response(418, text="teapot"))
    with pytest.raises(SonioxAPIError) as exc_info:
        client.files.list(limit=1)
    # Must NOT be one of the typed subclasses - exactly the base.
    assert type(exc_info.value) is SonioxAPIError
    assert exc_info.value.status_code == 418


# ---------------------------------------------------------------------------
# sync files.delete_all - mirror of the async-only test we already have
# ---------------------------------------------------------------------------


@respx.mock
def test_stt_get_or_none_returns_none_on_404(client: SonioxClient) -> None:
    """Direct sync test for ``stt.get_or_none`` - mirrors the files helper."""
    respx.get(f"{BASE_URL}/transcriptions/missing").mock(
        return_value=Response(404, text="")
    )
    assert client.stt.get_or_none("missing") is None


@respx.mock
def test_stt_get_or_none_reraises_non_404(client: SonioxClient) -> None:
    from soniox.errors import SonioxServerError

    respx.get(f"{BASE_URL}/transcriptions/boom").mock(return_value=Response(500))
    with pytest.raises(SonioxServerError):
        client.stt.get_or_none("boom")


@respx.mock
def test_stt_delete_if_exists_swallows_404(client: SonioxClient) -> None:
    respx.delete(f"{BASE_URL}/transcriptions/missing").mock(return_value=Response(404))
    client.stt.delete_if_exists("missing")  # must not raise


# ---------------------------------------------------------------------------
# TranslationConfig validator
# ---------------------------------------------------------------------------


def test_translation_config_one_way_requires_target_language() -> None:
    with pytest.raises(ValidationError, match="target_language is required"):
        TranslationConfig(type="one_way")


def test_translation_config_one_way_clears_two_way_fields() -> None:
    cfg = TranslationConfig(
        type="one_way", target_language="en", language_a="fr", language_b="de"
    )
    assert cfg.language_a is None
    assert cfg.language_b is None


def test_translation_config_two_way_requires_both_languages() -> None:
    with pytest.raises(ValidationError, match="language_a and language_b"):
        TranslationConfig(type="two_way", language_a="en")


def test_translation_config_two_way_clears_target_language() -> None:
    cfg = TranslationConfig(
        type="two_way", language_a="en", language_b="fr", target_language="de"
    )
    assert cfg.target_language is None


# ---------------------------------------------------------------------------
# CreateTranscriptionPayload validator
# ---------------------------------------------------------------------------


def test_create_transcription_payload_rejects_both_sources() -> None:
    with pytest.raises(ValidationError, match="Only one of audio_url or file_id"):
        CreateTranscriptionPayload(
            model="stt-async-v5",
            audio_url="https://a/b",
            file_id="f1",
        )


def test_create_transcription_payload_requires_a_source() -> None:
    with pytest.raises(ValidationError, match="Either audio_url or file_id"):
        CreateTranscriptionPayload(model="stt-async-v5")
