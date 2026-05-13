"""
Tests for high-level :class:`SttAPI` workflows that chain multiple REST
calls together (``transcribe_*``, ``wait``, ``transcribe_and_wait``, ...).

These helpers are where silent regressions bite hardest: any step in the
chain can break without the public method's signature changing. The tests
here pin down the expected sequence of wire calls and the resulting state.
"""

from __future__ import annotations

import io
from unittest.mock import patch

import pytest
import respx
from httpx import Response

from soniox.client import SonioxClient
from soniox.types import File, Transcription, TranscriptionTranscript, WebhookAuthConfig
from tests.helpers import API_KEY, BASE_URL, build

AUDIO_URL = "https://example.com/audio.mp3"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _transcription(status: str, *, tid: str = "t1", file_id: str | None = None) -> dict:
    """Build a ``Transcription`` JSON payload with a specific status."""
    t = build(Transcription)
    t.id = tid
    t.status = status  # type: ignore[assignment]
    t.file_id = file_id
    return t.model_dump(mode="json")


def _request_body(route: respx.Route) -> str:
    return route.calls.last.request.read().decode()


# ---------------------------------------------------------------------------
# stt.wait
# ---------------------------------------------------------------------------


@respx.mock
def test_wait_polls_until_completed(client: SonioxClient) -> None:
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

    with patch("time.sleep"):
        result = client.stt.wait("t1", interval_sec=0.0)

    assert route.call_count == 3
    assert result.status == "completed"


@respx.mock
def test_wait_returns_immediately_when_terminal(client: SonioxClient) -> None:
    """``wait`` must stop the moment the job is no longer queued/processing,
    even for terminal error statuses."""
    route = respx.get(f"{BASE_URL}/transcriptions/t1").mock(
        return_value=Response(200, json=_transcription("error"))
    )
    with patch("time.sleep") as sleep_mock:
        result = client.stt.wait("t1", interval_sec=1.0)

    assert route.call_count == 1
    sleep_mock.assert_not_called()
    assert result.status == "error"


@respx.mock
def test_wait_raises_timeout_error(client: SonioxClient) -> None:
    respx.get(f"{BASE_URL}/transcriptions/t1").mock(
        return_value=Response(200, json=_transcription("processing"))
    )
    with patch("time.sleep"):
        with pytest.raises(TimeoutError, match="t1"):
            client.stt.wait("t1", interval_sec=0.0, timeout_sec=0.0)


# ---------------------------------------------------------------------------
# transcribe_from_*
# ---------------------------------------------------------------------------


@respx.mock
def test_transcribe_from_url_posts_audio_url(client: SonioxClient) -> None:
    route = respx.post(f"{BASE_URL}/transcriptions").mock(
        return_value=Response(201, json=build(Transcription).model_dump(mode="json"))
    )
    client.stt.transcribe_from_url(audio_url=AUDIO_URL)
    assert f'"audio_url":"{AUDIO_URL}"' in _request_body(route)


@respx.mock
def test_transcribe_from_file_id_posts_file_id(client: SonioxClient) -> None:
    route = respx.post(f"{BASE_URL}/transcriptions").mock(
        return_value=Response(201, json=build(Transcription).model_dump(mode="json"))
    )
    client.stt.transcribe_from_file_id(file_id="f1")
    assert '"file_id":"f1"' in _request_body(route)


@respx.mock
def test_transcribe_from_file_uploads_then_creates(client: SonioxClient) -> None:
    """``transcribe_from_file`` is a two-step chain: upload → create."""
    uploaded = build(File)
    uploaded.id = "uploaded-id"

    upload = respx.post(f"{BASE_URL}/files").mock(
        return_value=Response(201, json=uploaded.model_dump(mode="json"))
    )
    create = respx.post(f"{BASE_URL}/transcriptions").mock(
        return_value=Response(201, json=build(Transcription).model_dump(mode="json"))
    )

    client.stt.transcribe_from_file(file=io.BytesIO(b"audio"), filename="clip.mp3")

    assert upload.call_count == 1
    assert create.call_count == 1
    assert '"file_id":"uploaded-id"' in _request_body(create)


# ---------------------------------------------------------------------------
# transcribe (dispatch + validation)
# ---------------------------------------------------------------------------


def test_transcribe_requires_one_input(client: SonioxClient) -> None:
    from soniox.errors import SonioxValidationError

    with pytest.raises(SonioxValidationError):
        client.stt.transcribe()
    with pytest.raises(SonioxValidationError):
        client.stt.transcribe(file=b"x", audio_url=AUDIO_URL)
    with pytest.raises(SonioxValidationError):
        client.stt.transcribe(file_id="f1", audio_url=AUDIO_URL)


@respx.mock
def test_transcribe_dispatches_by_input(client: SonioxClient) -> None:
    route = respx.post(f"{BASE_URL}/transcriptions").mock(
        return_value=Response(201, json=build(Transcription).model_dump(mode="json"))
    )

    client.stt.transcribe(audio_url=AUDIO_URL)
    assert f'"audio_url":"{AUDIO_URL}"' in _request_body(route)

    client.stt.transcribe(file_id="f1")
    assert '"file_id":"f1"' in _request_body(route)


# ---------------------------------------------------------------------------
# transcribe_and_wait
# ---------------------------------------------------------------------------


@respx.mock
def test_transcribe_and_wait_returns_completed_transcription(client: SonioxClient) -> None:
    respx.post(f"{BASE_URL}/transcriptions").mock(
        return_value=Response(201, json=_transcription("queued"))
    )
    respx.get(f"{BASE_URL}/transcriptions/t1").mock(
        return_value=Response(200, json=_transcription("completed"))
    )
    with patch("time.sleep"):
        result = client.stt.transcribe_and_wait(audio_url=AUDIO_URL)
    assert result.status == "completed"


@respx.mock
def test_transcribe_and_wait_deletes_transcription_and_file_when_requested(
    client: SonioxClient,
) -> None:
    respx.post(f"{BASE_URL}/transcriptions").mock(
        return_value=Response(201, json=_transcription("queued", file_id="f1"))
    )
    respx.get(f"{BASE_URL}/transcriptions/t1").mock(
        return_value=Response(200, json=_transcription("completed", file_id="f1"))
    )
    delete_t = respx.delete(f"{BASE_URL}/transcriptions/t1").mock(Response(204))
    delete_f = respx.delete(f"{BASE_URL}/files/f1").mock(Response(204))

    with patch("time.sleep"):
        client.stt.transcribe_and_wait(audio_url=AUDIO_URL, delete_after=True)

    assert delete_t.called
    assert delete_f.called


@respx.mock
def test_transcribe_and_wait_skips_file_delete_for_url_sources(
    client: SonioxClient,
) -> None:
    """If the transcription has no ``file_id``, only the transcription itself
    gets deleted (no file to clean up)."""
    respx.post(f"{BASE_URL}/transcriptions").mock(
        return_value=Response(201, json=_transcription("queued", file_id=None))
    )
    respx.get(f"{BASE_URL}/transcriptions/t1").mock(
        return_value=Response(200, json=_transcription("completed", file_id=None))
    )
    delete_t = respx.delete(f"{BASE_URL}/transcriptions/t1").mock(Response(204))
    # Any unexpected call to /files/* would raise because no route matches.

    with patch("time.sleep"):
        client.stt.transcribe_and_wait(audio_url=AUDIO_URL, delete_after=True)

    assert delete_t.called


@respx.mock
def test_transcribe_and_wait_with_tokens_deletes_when_requested(
    client: SonioxClient,
) -> None:
    """``delete_after=True`` must clean up both the transcription and the
    uploaded source file *after* the transcript has been fetched."""
    respx.post(f"{BASE_URL}/transcriptions").mock(
        return_value=Response(201, json=_transcription("queued", file_id="f1"))
    )
    respx.get(f"{BASE_URL}/transcriptions/t1").mock(
        return_value=Response(200, json=_transcription("completed", file_id="f1"))
    )
    respx.get(f"{BASE_URL}/transcriptions/t1/transcript").mock(
        return_value=Response(200, json=build(TranscriptionTranscript).model_dump(mode="json"))
    )
    delete_t = respx.delete(f"{BASE_URL}/transcriptions/t1").mock(Response(204))
    delete_f = respx.delete(f"{BASE_URL}/files/f1").mock(Response(204))

    with patch("time.sleep"):
        client.stt.transcribe_and_wait_with_tokens(
            audio_url=AUDIO_URL, delete_after=True
        )

    assert delete_t.called
    assert delete_f.called


@respx.mock
def test_transcribe_and_wait_with_tokens_returns_transcript(client: SonioxClient) -> None:
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

    with patch("time.sleep"):
        result = client.stt.transcribe_and_wait_with_tokens(audio_url=AUDIO_URL)

    assert fetch.called
    assert result == transcript


# ---------------------------------------------------------------------------
# transcribe_file_with_webhook
# ---------------------------------------------------------------------------


@respx.mock
def test_transcribe_file_with_webhook_uses_client_default_auth() -> None:
    with SonioxClient(api_key=API_KEY, webhook_secret="wh-secret") as client:
        uploaded = build(File)
        uploaded.id = "uploaded-id"

        respx.post(f"{BASE_URL}/files").mock(
            return_value=Response(201, json=uploaded.model_dump(mode="json"))
        )
        create = respx.post(f"{BASE_URL}/transcriptions").mock(
            return_value=Response(201, json=build(Transcription).model_dump(mode="json"))
        )

        client.stt.transcribe_file_with_webhook(
            file=io.BytesIO(b"audio"),
            filename="clip.mp3",
            webhook_url="https://me.com/hook",
        )

    body = _request_body(create)
    assert '"file_id":"uploaded-id"' in body
    assert '"webhook_url":"https://me.com/hook"' in body
    assert '"webhook_auth_header_name":"X-Soniox-Webhook-Secret"' in body
    assert '"webhook_auth_header_value":"wh-secret"' in body


@respx.mock
def test_transcribe_file_with_webhook_accepts_per_call_auth() -> None:
    with SonioxClient(api_key=API_KEY) as client:
        respx.post(f"{BASE_URL}/files").mock(
            return_value=Response(201, json=build(File).model_dump(mode="json"))
        )
        create = respx.post(f"{BASE_URL}/transcriptions").mock(
            return_value=Response(201, json=build(Transcription).model_dump(mode="json"))
        )

        client.stt.transcribe_file_with_webhook(
            file=io.BytesIO(b"audio"),
            filename="clip.mp3",
            webhook_url="https://me.com/hook",
            webhook_auth=WebhookAuthConfig(name="X-Custom", value="v"),
        )

    body = _request_body(create)
    assert '"webhook_auth_header_name":"X-Custom"' in body
    assert '"webhook_auth_header_value":"v"' in body
