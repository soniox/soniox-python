"""Unit tests for the Voices (voice-cloning) REST API, sync and async."""

from __future__ import annotations

import json
from io import BytesIO

import respx
from httpx import Response

from soniox.client import AsyncSonioxClient, SonioxClient

BASE = "https://api.soniox.com/v1"

_VOICE = {
    "id": "v-123",
    "name": "My Voice",
    "filename": "clip.mp3",
    "created_at": "2026-01-01T00:00:00Z",
    "models": [
        {"model": "tts-rt-v1", "status": "ready", "error_type": None, "error_message": None}
    ],
}


@respx.mock
def test_list_returns_voices(client: SonioxClient) -> None:
    route = respx.get(f"{BASE}/voices").mock(
        return_value=Response(200, json={"voices": [_VOICE], "next_page_cursor": None})
    )

    result = client.voices.list(limit=5)

    assert route.calls.last.request.url.params["limit"] == "5"
    assert len(result.voices) == 1
    assert result.voices[0].id == "v-123"
    assert result.voices[0].models[0].status == "ready"


@respx.mock
def test_list_all_paginates(client: SonioxClient) -> None:
    page2 = {**_VOICE, "id": "v-456"}
    respx.get(f"{BASE}/voices").mock(
        side_effect=[
            Response(200, json={"voices": [_VOICE], "next_page_cursor": "next"}),
            Response(200, json={"voices": [page2], "next_page_cursor": None}),
        ]
    )

    ids = [v.id for v in client.voices.list_all()]

    assert ids == ["v-123", "v-456"]


@respx.mock
def test_count(client: SonioxClient) -> None:
    respx.get(f"{BASE}/voices/count").mock(return_value=Response(200, json={"total": 7}))
    assert client.voices.count().total == 7


@respx.mock
def test_get_or_none_returns_none_on_404(client: SonioxClient) -> None:
    respx.get(f"{BASE}/voices/missing").mock(
        return_value=Response(404, json={"status_code": 404, "error_type": "not_found",
                                         "message": "x", "validation_errors": [],
                                         "request_id": "r"})
    )
    assert client.voices.get_or_none("missing") is None


@respx.mock
def test_create_sends_multipart_name_and_file(client: SonioxClient) -> None:
    route = respx.post(f"{BASE}/voices").mock(return_value=Response(201, json=_VOICE))

    voice = client.voices.create(BytesIO(b"audio-bytes"), name="My Voice", filename="clip.mp3")

    req = route.calls.last.request
    assert "multipart/form-data" in req.headers["Content-Type"]
    body = req.content.decode("latin-1")
    assert "My Voice" in body and "audio-bytes" in body
    assert voice.id == "v-123"


@respx.mock
def test_recompute_sends_model_in_body(client: SonioxClient) -> None:
    route = respx.post(f"{BASE}/voices/v-123/recompute").mock(
        return_value=Response(200, json=_VOICE)
    )

    client.voices.recompute("v-123", model="tts-rt-v1")

    assert json.loads(route.calls.last.request.content) == {"model": "tts-rt-v1"}


@respx.mock
def test_recompute_omits_model_when_none(client: SonioxClient) -> None:
    route = respx.post(f"{BASE}/voices/v-123/recompute").mock(
        return_value=Response(200, json=_VOICE)
    )

    client.voices.recompute("v-123")

    assert json.loads(route.calls.last.request.content) == {}


@respx.mock
def test_delete_if_exists_ignores_404(client: SonioxClient) -> None:
    respx.delete(f"{BASE}/voices/gone").mock(
        return_value=Response(404, json={"status_code": 404, "error_type": "not_found",
                                         "message": "x", "validation_errors": [],
                                         "request_id": "r"})
    )
    assert client.voices.delete_if_exists("gone") is None


@respx.mock
async def test_async_create_and_get(async_client: AsyncSonioxClient) -> None:
    respx.post(f"{BASE}/voices").mock(return_value=Response(201, json=_VOICE))
    respx.get(f"{BASE}/voices/v-123").mock(return_value=Response(200, json=_VOICE))

    created = await async_client.voices.create(BytesIO(b"a"), name="My Voice")
    fetched = await async_client.voices.get("v-123")

    assert created.id == fetched.id == "v-123"
    assert fetched.models[0].model == "tts-rt-v1"
