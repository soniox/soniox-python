"""Unit tests for the asynchronous Text-to-Speech REST API."""

from __future__ import annotations

import json
from io import BytesIO
from pathlib import Path

import pytest
import respx
from httpx import Response

from soniox.client import AsyncSonioxClient
from soniox.errors import SonioxAPIError
from soniox.types import CreateTtsConfig

TTS_BASE_URL = "https://tts-rt.soniox.com"
_AUDIO = b"RIFFsynth-audio"


def _mock_tts_endpoint(content: bytes = _AUDIO) -> respx.Route:
    return respx.post(f"{TTS_BASE_URL}/tts").mock(
        return_value=Response(200, content=content)
    )


@respx.mock
async def test_generate_returns_audio_bytes(async_client: AsyncSonioxClient) -> None:
    route = _mock_tts_endpoint()

    audio = await async_client.tts.generate(text="hello", voice="Adrian")

    assert audio == _AUDIO
    body = json.loads(route.calls.last.request.content)
    assert body["text"] == "hello"
    assert body["voice"] == "Adrian"


@respx.mock
async def test_generate_overrides_via_config(async_client: AsyncSonioxClient) -> None:
    route = _mock_tts_endpoint()
    config = CreateTtsConfig(model="custom-model", language="de")

    await async_client.tts.generate(
        text="hallo",
        voice="Adrian",
        audio_format="mp3",
        config=config,
    )

    body = json.loads(route.calls.last.request.content)
    assert body["model"] == "custom-model"
    assert body["language"] == "de"
    assert body["audio_format"] == "mp3"


@respx.mock
async def test_generate_to_file_writes_path(
    async_client: AsyncSonioxClient, tmp_path: Path
) -> None:
    _mock_tts_endpoint()
    out = tmp_path / "out.wav"

    written = await async_client.tts.generate_to_file(out, text="hi", voice="Adrian")

    assert written == len(_AUDIO)
    assert out.read_bytes() == _AUDIO


@respx.mock
async def test_generate_to_file_writes_str_path(
    async_client: AsyncSonioxClient, tmp_path: Path
) -> None:
    _mock_tts_endpoint()
    out = tmp_path / "out.wav"

    written = await async_client.tts.generate_to_file(
        str(out), text="hi", voice="Adrian"
    )

    assert written == len(_AUDIO)
    assert out.read_bytes() == _AUDIO


@respx.mock
async def test_generate_to_file_writes_binaryio(async_client: AsyncSonioxClient) -> None:
    _mock_tts_endpoint()
    buf = BytesIO()

    written = await async_client.tts.generate_to_file(buf, text="hi", voice="Adrian")

    assert written == len(_AUDIO)
    assert buf.getvalue() == _AUDIO


@respx.mock
async def test_generate_raises_on_api_error(async_client: AsyncSonioxClient) -> None:
    respx.post(f"{TTS_BASE_URL}/tts").mock(
        return_value=Response(
            500,
            json={
                "status_code": 500,
                "error_type": "internal_error",
                "message": "boom",
                "request_id": "req_1",
            },
        )
    )

    with pytest.raises(SonioxAPIError):
        await async_client.tts.generate(text="hi", voice="Adrian")
