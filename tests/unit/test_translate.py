"""Tests for the translate kwargs validation and the translate* wire formats."""

from __future__ import annotations

import io
import json
from unittest.mock import patch

import pytest
import respx
from httpx import Response

from soniox.api._utils import build_translate_config
from soniox.client import AsyncSonioxClient, SonioxClient
from soniox.errors import SonioxValidationError
from soniox.types import (
    CreateTranscriptionConfig,
    File,
    Transcription,
    TranscriptionTranscript,
    TranslationConfig,
)
from tests.helpers import BASE_URL, build


AUDIO_URL = "https://example.com/a.mp3"


def _transcription(status: str, *, tid: str = "t1", file_id: str | None = None) -> dict:
    t = build(Transcription)
    t.id = tid
    t.status = status  # type: ignore[assignment]
    t.file_id = file_id
    return t.model_dump(mode="json")


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


# ---------------------------------------------------------------------------
# variant wire tests: translate_from_url / _from_file_id / _from_file
# ---------------------------------------------------------------------------


@respx.mock
async def test_async_translate_from_url(async_client: AsyncSonioxClient) -> None:
    route = respx.post(f"{BASE_URL}/transcriptions").mock(
        return_value=Response(201, json=build(Transcription).model_dump(mode="json"))
    )
    await async_client.stt.translate_from_url(to="fr", audio_url=AUDIO_URL)
    body = json.loads(route.calls.last.request.read())
    assert body["audio_url"] == AUDIO_URL
    assert body["translation"] == {"type": "one_way", "target_language": "fr"}


@respx.mock
async def test_async_translate_from_file_id(async_client: AsyncSonioxClient) -> None:
    route = respx.post(f"{BASE_URL}/transcriptions").mock(
        return_value=Response(201, json=build(Transcription).model_dump(mode="json"))
    )
    await async_client.stt.translate_from_file_id(to="fr", file_id="f1")
    body = json.loads(route.calls.last.request.read())
    assert body["file_id"] == "f1"
    assert body["translation"] == {"type": "one_way", "target_language": "fr"}


@respx.mock
async def test_async_translate_from_file_uploads_then_creates(
    async_client: AsyncSonioxClient,
) -> None:
    uploaded = build(File)
    uploaded.id = "uploaded-id"

    upload = respx.post(f"{BASE_URL}/files").mock(
        return_value=Response(201, json=uploaded.model_dump(mode="json"))
    )
    create = respx.post(f"{BASE_URL}/transcriptions").mock(
        return_value=Response(201, json=build(Transcription).model_dump(mode="json"))
    )

    await async_client.stt.translate_from_file(
        to="fr", file=io.BytesIO(b"audio"), filename="clip.mp3"
    )

    assert upload.call_count == 1
    assert create.call_count == 1
    body = json.loads(create.calls.last.request.read())
    assert body["file_id"] == "uploaded-id"
    assert body["translation"] == {"type": "one_way", "target_language": "fr"}


# ---------------------------------------------------------------------------
# translate_and_wait and translate_and_wait_with_tokens
# ---------------------------------------------------------------------------


@respx.mock
async def test_async_translate_and_wait_returns_completed(
    async_client: AsyncSonioxClient,
) -> None:
    create = respx.post(f"{BASE_URL}/transcriptions").mock(
        return_value=Response(201, json=_transcription("queued"))
    )
    respx.get(f"{BASE_URL}/transcriptions/t1").mock(
        return_value=Response(200, json=_transcription("completed"))
    )
    with patch("asyncio.sleep"):
        result = await async_client.stt.translate_and_wait(to="fr", audio_url=AUDIO_URL)

    assert result.status == "completed"
    body = json.loads(create.calls.last.request.read())
    assert body["translation"] == {"type": "one_way", "target_language": "fr"}


@respx.mock
async def test_async_translate_and_wait_with_tokens_returns_transcript(
    async_client: AsyncSonioxClient,
) -> None:
    create = respx.post(f"{BASE_URL}/transcriptions").mock(
        return_value=Response(201, json=_transcription("queued"))
    )
    respx.get(f"{BASE_URL}/transcriptions/t1").mock(
        return_value=Response(200, json=_transcription("completed"))
    )
    respx.get(f"{BASE_URL}/transcriptions/t1/transcript").mock(
        return_value=Response(
            200, json=build(TranscriptionTranscript).model_dump(mode="json")
        )
    )
    with patch("asyncio.sleep"):
        result = await async_client.stt.translate_and_wait_with_tokens(
            to="fr", audio_url=AUDIO_URL
        )

    assert isinstance(result, TranscriptionTranscript)
    body = json.loads(create.calls.last.request.read())
    assert body["translation"] == {"type": "one_way", "target_language": "fr"}


# ---------------------------------------------------------------------------
# sync translate parity
# ---------------------------------------------------------------------------


@respx.mock
def test_sync_translate_sends_one_way_config(client: SonioxClient) -> None:
    route = respx.post(f"{BASE_URL}/transcriptions").mock(
        return_value=Response(201, json=build(Transcription).model_dump(mode="json"))
    )
    client.stt.translate(to="es", audio_url=AUDIO_URL)
    body = json.loads(route.calls.last.request.read())
    assert body["translation"] == {"type": "one_way", "target_language": "es"}
    assert body["enable_language_identification"] is True


@respx.mock
def test_sync_translate_variants_dispatch(client: SonioxClient) -> None:
    """Exercises each sync translate_* variant's body in one test."""
    uploaded = build(File)
    uploaded.id = "uploaded-id"
    respx.post(f"{BASE_URL}/files").mock(
        return_value=Response(201, json=uploaded.model_dump(mode="json"))
    )
    respx.post(f"{BASE_URL}/transcriptions").mock(
        return_value=Response(201, json=_transcription("queued"))
    )
    respx.get(f"{BASE_URL}/transcriptions/t1").mock(
        return_value=Response(200, json=_transcription("completed"))
    )
    respx.get(f"{BASE_URL}/transcriptions/t1/transcript").mock(
        return_value=Response(
            200, json=build(TranscriptionTranscript).model_dump(mode="json")
        )
    )

    client.stt.translate_from_url(to="fr", audio_url=AUDIO_URL)
    client.stt.translate_from_file_id(to="fr", file_id="f1")
    client.stt.translate_from_file(to="fr", file=io.BytesIO(b"audio"), filename="a.mp3")

    with patch("time.sleep"):
        completed = client.stt.translate_and_wait(to="fr", audio_url=AUDIO_URL)
        transcript = client.stt.translate_and_wait_with_tokens(to="fr", audio_url=AUDIO_URL)

    assert completed.status == "completed"
    assert isinstance(transcript, TranscriptionTranscript)
