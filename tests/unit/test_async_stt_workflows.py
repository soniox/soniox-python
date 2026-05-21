"""
Async mirror of :mod:`tests.unit.test_stt_workflows`.

The async STT helpers (``AsyncSttAPI.wait``, ``transcribe_*``,
``transcribe_and_wait*``, ``transcribe_file_with_webhook``) are essentially
line-by-line translations of their sync counterparts with ``await`` added.
This file verifies that both halves of the API actually behave the same on
the wire.
"""

from __future__ import annotations

import io
from unittest.mock import patch

import pytest
import respx
from httpx import Response

from soniox.client import AsyncSonioxClient
from soniox.types import File, Transcription, TranscriptionTranscript, WebhookAuthConfig
from tests.helpers import API_KEY, BASE_URL, build

AUDIO_URL = "https://example.com/audio.mp3"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _transcription(status: str, *, tid: str = "t1", file_id: str | None = None) -> dict:
    t = build(Transcription)
    t.id = tid
    t.status = status  # type: ignore[assignment]
    t.file_id = file_id
    return t.model_dump(mode="json")


def _request_body(route: respx.Route) -> str:
    return route.calls.last.request.read().decode()


# ---------------------------------------------------------------------------
# async wait
# ---------------------------------------------------------------------------


@respx.mock
async def test_async_wait_polls_until_completed(async_client: AsyncSonioxClient) -> None:
    responses = iter(
        [
            Response(200, json=_transcription("queued")),
            Response(200, json=_transcription("processing")),
            Response(200, json=_transcription("completed")),
        ]
    )
    route = respx.get(f"{BASE_URL}/transcriptions/t1").mock(
        side_effect=lambda req: next(responses)
    )

    with patch("asyncio.sleep"):
        result = await async_client.stt.wait("t1", interval_sec=0.0)

    assert route.call_count == 3
    assert result.status == "completed"


@respx.mock
async def test_async_wait_stops_on_terminal_status(async_client: AsyncSonioxClient) -> None:
    route = respx.get(f"{BASE_URL}/transcriptions/t1").mock(
        return_value=Response(200, json=_transcription("error"))
    )
    with patch("asyncio.sleep") as sleep_mock:
        result = await async_client.stt.wait("t1", interval_sec=1.0)

    assert route.call_count == 1
    sleep_mock.assert_not_called()
    assert result.status == "error"


@respx.mock
async def test_async_wait_raises_timeout(async_client: AsyncSonioxClient) -> None:
    respx.get(f"{BASE_URL}/transcriptions/t1").mock(
        return_value=Response(200, json=_transcription("processing"))
    )
    with patch("asyncio.sleep"):
        with pytest.raises(TimeoutError, match="t1"):
            await async_client.stt.wait("t1", interval_sec=0.0, timeout_sec=0.0)


# ---------------------------------------------------------------------------
# async transcribe_from_*
# ---------------------------------------------------------------------------


@respx.mock
async def test_async_transcribe_from_url(async_client: AsyncSonioxClient) -> None:
    route = respx.post(f"{BASE_URL}/transcriptions").mock(
        return_value=Response(201, json=build(Transcription).model_dump(mode="json"))
    )
    await async_client.stt.transcribe_from_url(audio_url=AUDIO_URL)
    assert f'"audio_url":"{AUDIO_URL}"' in _request_body(route)


@respx.mock
async def test_async_transcribe_from_file_id(async_client: AsyncSonioxClient) -> None:
    route = respx.post(f"{BASE_URL}/transcriptions").mock(
        return_value=Response(201, json=build(Transcription).model_dump(mode="json"))
    )
    await async_client.stt.transcribe_from_file_id(file_id="f1")
    assert '"file_id":"f1"' in _request_body(route)


@respx.mock
async def test_async_transcribe_from_file_uploads_then_creates(
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

    await async_client.stt.transcribe_from_file(
        file=io.BytesIO(b"audio"), filename="clip.mp3"
    )

    assert upload.call_count == 1
    assert create.call_count == 1
    assert '"file_id":"uploaded-id"' in _request_body(create)


# ---------------------------------------------------------------------------
# async transcribe (dispatch + validation)
# ---------------------------------------------------------------------------


async def test_async_transcribe_requires_one_input(async_client: AsyncSonioxClient) -> None:
    from soniox.errors import SonioxValidationError

    with pytest.raises(SonioxValidationError):
        await async_client.stt.transcribe()
    with pytest.raises(SonioxValidationError):
        await async_client.stt.transcribe(file=b"x", audio_url=AUDIO_URL)
    with pytest.raises(SonioxValidationError):
        await async_client.stt.transcribe(file_id="f1", audio_url=AUDIO_URL)


@respx.mock
async def test_async_transcribe_dispatches_by_input(async_client: AsyncSonioxClient) -> None:
    uploaded = build(File)
    uploaded.id = "uploaded-id"
    respx.post(f"{BASE_URL}/files").mock(
        return_value=Response(201, json=uploaded.model_dump(mode="json"))
    )
    route = respx.post(f"{BASE_URL}/transcriptions").mock(
        return_value=Response(201, json=build(Transcription).model_dump(mode="json"))
    )

    await async_client.stt.transcribe(audio_url=AUDIO_URL)
    assert f'"audio_url":"{AUDIO_URL}"' in _request_body(route)

    await async_client.stt.transcribe(file_id="f1")
    assert '"file_id":"f1"' in _request_body(route)

    await async_client.stt.transcribe(file=io.BytesIO(b"audio"), filename="clip.mp3")
    assert '"file_id":"uploaded-id"' in _request_body(route)


async def test_async_create_rejects_both_audio_url_and_file_id(
    async_client: AsyncSonioxClient,
) -> None:
    from soniox.errors import SonioxValidationError

    with pytest.raises(SonioxValidationError):
        await async_client.stt.create(audio_url=AUDIO_URL, file_id="f1")


# ---------------------------------------------------------------------------
# async transcribe_and_wait
# ---------------------------------------------------------------------------


@respx.mock
async def test_async_transcribe_and_wait_happy_path(async_client: AsyncSonioxClient) -> None:
    respx.post(f"{BASE_URL}/transcriptions").mock(
        return_value=Response(201, json=_transcription("queued"))
    )
    respx.get(f"{BASE_URL}/transcriptions/t1").mock(
        return_value=Response(200, json=_transcription("completed"))
    )
    with patch("asyncio.sleep"):
        result = await async_client.stt.transcribe_and_wait(audio_url=AUDIO_URL)
    assert result.status == "completed"


@respx.mock
async def test_async_transcribe_and_wait_deletes_both(async_client: AsyncSonioxClient) -> None:
    respx.post(f"{BASE_URL}/transcriptions").mock(
        return_value=Response(201, json=_transcription("queued", file_id="f1"))
    )
    respx.get(f"{BASE_URL}/transcriptions/t1").mock(
        return_value=Response(200, json=_transcription("completed", file_id="f1"))
    )
    delete_t = respx.delete(f"{BASE_URL}/transcriptions/t1").mock(Response(204))
    delete_f = respx.delete(f"{BASE_URL}/files/f1").mock(Response(204))

    with patch("asyncio.sleep"):
        await async_client.stt.transcribe_and_wait(audio_url=AUDIO_URL, delete_after=True)

    assert delete_t.called
    assert delete_f.called


@respx.mock
async def test_async_transcribe_and_wait_skips_file_delete_for_url_sources(
    async_client: AsyncSonioxClient,
) -> None:
    respx.post(f"{BASE_URL}/transcriptions").mock(
        return_value=Response(201, json=_transcription("queued", file_id=None))
    )
    respx.get(f"{BASE_URL}/transcriptions/t1").mock(
        return_value=Response(200, json=_transcription("completed", file_id=None))
    )
    delete_t = respx.delete(f"{BASE_URL}/transcriptions/t1").mock(Response(204))

    with patch("asyncio.sleep"):
        await async_client.stt.transcribe_and_wait(audio_url=AUDIO_URL, delete_after=True)

    assert delete_t.called


@respx.mock
async def test_async_transcribe_and_wait_with_tokens_deletes_when_requested(
    async_client: AsyncSonioxClient,
) -> None:
    respx.post(f"{BASE_URL}/transcriptions").mock(
        return_value=Response(201, json=_transcription("queued", file_id="f1"))
    )
    respx.get(f"{BASE_URL}/transcriptions/t1").mock(
        return_value=Response(200, json=_transcription("completed", file_id="f1"))
    )
    respx.get(f"{BASE_URL}/transcriptions/t1/transcript").mock(
        return_value=Response(
            200, json=build(TranscriptionTranscript).model_dump(mode="json")
        )
    )
    delete_t = respx.delete(f"{BASE_URL}/transcriptions/t1").mock(Response(204))
    delete_f = respx.delete(f"{BASE_URL}/files/f1").mock(Response(204))

    with patch("asyncio.sleep"):
        await async_client.stt.transcribe_and_wait_with_tokens(
            audio_url=AUDIO_URL, delete_after=True
        )

    assert delete_t.called
    assert delete_f.called


@respx.mock
async def test_async_transcribe_and_wait_with_tokens(async_client: AsyncSonioxClient) -> None:
    respx.post(f"{BASE_URL}/transcriptions").mock(
        return_value=Response(201, json=_transcription("queued"))
    )
    respx.get(f"{BASE_URL}/transcriptions/t1").mock(
        return_value=Response(200, json=_transcription("completed"))
    )
    transcript = build(TranscriptionTranscript)
    fetch = respx.get(f"{BASE_URL}/transcriptions/t1/transcript").mock(
        return_value=Response(200, json=transcript.model_dump(mode="json"))
    )

    with patch("asyncio.sleep"):
        result = await async_client.stt.transcribe_and_wait_with_tokens(audio_url=AUDIO_URL)

    assert fetch.called
    assert result == transcript


# ---------------------------------------------------------------------------
# async transcribe_file_with_webhook
# ---------------------------------------------------------------------------


@respx.mock
async def test_async_transcribe_file_with_webhook_uses_client_default_auth() -> None:
    async with AsyncSonioxClient(api_key=API_KEY, webhook_secret="wh-secret") as client:
        uploaded = build(File)
        uploaded.id = "uploaded-id"

        respx.post(f"{BASE_URL}/files").mock(
            return_value=Response(201, json=uploaded.model_dump(mode="json"))
        )
        create = respx.post(f"{BASE_URL}/transcriptions").mock(
            return_value=Response(201, json=build(Transcription).model_dump(mode="json"))
        )

        await client.stt.transcribe_file_with_webhook(
            file=io.BytesIO(b"audio"),
            filename="clip.mp3",
            webhook_url="https://me.com/hook",
        )

    body = _request_body(create)
    assert '"file_id":"uploaded-id"' in body
    assert '"webhook_auth_header_name":"X-Soniox-Webhook-Secret"' in body
    assert '"webhook_auth_header_value":"wh-secret"' in body


@respx.mock
async def test_async_transcribe_file_with_webhook_accepts_per_call_auth() -> None:
    async with AsyncSonioxClient(api_key=API_KEY) as client:
        respx.post(f"{BASE_URL}/files").mock(
            return_value=Response(201, json=build(File).model_dump(mode="json"))
        )
        create = respx.post(f"{BASE_URL}/transcriptions").mock(
            return_value=Response(201, json=build(Transcription).model_dump(mode="json"))
        )

        await client.stt.transcribe_file_with_webhook(
            file=io.BytesIO(b"audio"),
            filename="clip.mp3",
            webhook_url="https://me.com/hook",
            webhook_auth=WebhookAuthConfig(name="X-Custom", value="v"),
        )

    body = _request_body(create)
    assert '"webhook_auth_header_name":"X-Custom"' in body
    assert '"webhook_auth_header_value":"v"' in body
