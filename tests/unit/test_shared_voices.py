"""
Tests for ``client.voices.list_shared`` - list filters go on the wire as
repeated query params, and unset filters are omitted.
"""

from __future__ import annotations

import pytest
import respx
from httpx import Response
from pydantic import ValidationError

from soniox.client import AsyncSonioxClient, SonioxClient
from tests.helpers import BASE_URL

SHARED_VOICES_URL = f"{BASE_URL}/shared-voices"


@respx.mock
def test_list_filters_are_repeated_query_params(client: SonioxClient) -> None:
    route = respx.get(SHARED_VOICES_URL).mock(return_value=Response(200, json={"voices": []}))

    client.voices.list_shared("tts-rt-v2", use_case=["narration", "conversational"])

    params = route.calls.last.request.url.params
    assert params.get_list("use_case") == ["narration", "conversational"]
    assert set(params.keys()) == {"model", "use_case", "limit"}


def _voice(voice_id: str) -> dict:
    return {
        "id": voice_id,
        "description": "A calm voice.",
        "gender": "female",
        "age": "young",
        "accent": "british",
        "use_case": ["narration"],
        "style": ["calm"],
    }


@respx.mock
def test_list_all_follows_cursor_and_keeps_filters(client: SonioxClient) -> None:
    route = respx.get(SHARED_VOICES_URL).mock(
        side_effect=[
            Response(200, json={"voices": [_voice("A")], "next_page_cursor": "page-2"}),
            Response(200, json={"voices": [_voice("B")], "next_page_cursor": None}),
        ]
    )

    voices = list(client.voices.list_all_shared("tts-rt-v2", gender="female"))

    assert [v.id for v in voices] == ["A", "B"]
    second = route.calls[1].request.url.params
    assert second["cursor"] == "page-2"
    assert second["gender"] == "female"


@pytest.mark.asyncio
@respx.mock
async def test_async_list_all_follows_cursor(async_client: AsyncSonioxClient) -> None:
    respx.get(SHARED_VOICES_URL).mock(
        side_effect=[
            Response(200, json={"voices": [_voice("A")], "next_page_cursor": "page-2"}),
            Response(200, json={"voices": [_voice("B")]}),
        ]
    )

    voices = [v async for v in async_client.voices.list_all_shared("tts-rt-v2")]

    assert [v.id for v in voices] == ["A", "B"]


@pytest.mark.parametrize(
    "kwargs",
    [
        {"model": "m" * 65},
        {"accent": "a" * 41},
        {"style": ["calm"] * 11},
        {"use_case": ["u" * 41]},
    ],
)
@respx.mock
def test_schema_limits_rejected_before_request(client: SonioxClient, kwargs: dict) -> None:
    route = respx.get(SHARED_VOICES_URL).mock(return_value=Response(200, json={"voices": []}))
    model = kwargs.pop("model", "tts-rt-v2")

    with pytest.raises(ValidationError):
        client.voices.list_shared(model, **kwargs)

    assert not route.called
