"""Tests for the translate kwargs validation and the translate() wire format."""

from __future__ import annotations

import json

import pytest
import respx
from httpx import Response

from soniox.api._utils import build_translate_config
from soniox.client import AsyncSonioxClient
from soniox.errors import SonioxValidationError
from soniox.types import (
    CreateTranscriptionConfig,
    Transcription,
    TranslationConfig,
)
from tests.helpers import BASE_URL, build


# ---------------------------------------------------------------------------
# build_translate_config
# ---------------------------------------------------------------------------


def test_one_way_sets_translation_and_lang_id() -> None:
    cfg = build_translate_config(to="fr", source=None, between=None, config=None)
    assert cfg.translation == TranslationConfig(type="one_way", target_language="fr")
    assert cfg.enable_language_identification is True
    assert cfg.language_hints is None


def test_one_way_with_source_sets_strict_hint() -> None:
    cfg = build_translate_config(to="fr", source="en", between=None, config=None)
    assert cfg.language_hints == ["en"]
    assert cfg.language_hints_strict is True


def test_two_way_sets_both_language_codes() -> None:
    cfg = build_translate_config(to=None, source=None, between=("en", "fr"), config=None)
    assert cfg.translation == TranslationConfig(type="two_way", language_a="en", language_b="fr")
    assert cfg.enable_language_identification is True


def test_preserves_user_supplied_config_fields() -> None:
    user = CreateTranscriptionConfig(model="custom-model", enable_speaker_diarization=True)
    cfg = build_translate_config(to="es", source=None, between=None, config=user)
    assert cfg.model == "custom-model"
    assert cfg.enable_speaker_diarization is True
    assert cfg.translation == TranslationConfig(type="one_way", target_language="es")
    # original is untouched
    assert user.translation is None


def test_requires_exactly_one_of_to_or_between_none() -> None:
    with pytest.raises(SonioxValidationError):
        build_translate_config(to=None, source=None, between=None, config=None)


def test_requires_exactly_one_of_to_or_between_both() -> None:
    with pytest.raises(SonioxValidationError):
        build_translate_config(to="fr", source=None, between=("en", "fr"), config=None)


def test_source_without_to_rejected() -> None:
    with pytest.raises(SonioxValidationError):
        build_translate_config(to=None, source="en", between=("en", "fr"), config=None)


def test_two_way_rejects_non_two_char_codes() -> None:
    # Pydantic LanguageCode constraint kicks in on TranslationConfig construction.
    with pytest.raises(ValueError):
        build_translate_config(to=None, source=None, between=("eng", "fr"), config=None)


# ---------------------------------------------------------------------------
# wire-level: translate() actually sends translation + language ID
# ---------------------------------------------------------------------------


@respx.mock
async def test_async_translate_sends_one_way_config(async_client: AsyncSonioxClient) -> None:
    transcription = build(Transcription)

    route = respx.post(f"{BASE_URL}/transcriptions").mock(
        return_value=Response(200, json=transcription.model_dump(mode="json"))
    )

    await async_client.stt.translate(
        to="fr",
        source="en",
        audio_url="https://example.com/a.mp3",
    )
    body = json.loads(route.calls.last.request.read())
    assert body["translation"] == {"type": "one_way", "target_language": "fr"}
    assert body["enable_language_identification"] is True
    assert body["language_hints"] == ["en"]
    assert body["language_hints_strict"] is True


@respx.mock
async def test_async_translate_sends_two_way_config(async_client: AsyncSonioxClient) -> None:
    transcription = build(Transcription)

    route = respx.post(f"{BASE_URL}/transcriptions").mock(
        return_value=Response(200, json=transcription.model_dump(mode="json"))
    )

    await async_client.stt.translate(
        between=("en", "fr"),
        audio_url="https://example.com/a.mp3",
    )
    body = json.loads(route.calls.last.request.read())
    assert body["translation"] == {"type": "two_way", "language_a": "en", "language_b": "fr"}
    assert body["enable_language_identification"] is True
    assert "language_hints" not in body
