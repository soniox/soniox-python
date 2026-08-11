"""Unit tests for the synchronous Text-to-Speech REST API."""

from __future__ import annotations

import json
from io import BytesIO
from pathlib import Path

import pytest
import respx
from httpx import Response

from soniox.client import SonioxClient
from soniox.types import CreateTtsConfig

TTS_BASE_URL = "https://tts-rt.soniox.com"
_AUDIO = b"RIFFsynth-audio"


def _mock_tts_endpoint(content: bytes = _AUDIO) -> respx.Route:
    return respx.post(f"{TTS_BASE_URL}/tts").mock(
        return_value=Response(200, content=content)
    )


@respx.mock
def test_generate_returns_audio_bytes(client: SonioxClient) -> None:
    route = _mock_tts_endpoint()

    audio = client.tts.generate(text="hello", voice="Adrian", language="en")

    assert audio == _AUDIO
    body = json.loads(route.calls.last.request.content)
    assert body["text"] == "hello"
    assert body["voice"] == "Adrian"
    assert body["language"] == "en"
    assert body["audio_format"] == "wav"


@respx.mock
def test_generate_sends_speed_from_config(client: SonioxClient) -> None:
    route = _mock_tts_endpoint()

    client.tts.generate(text="hi", voice="Adrian", language="en", config=CreateTtsConfig(speed=1.2))

    assert json.loads(route.calls.last.request.content)["speed"] == 1.2


@respx.mock
def test_generate_sends_reduce_silence_from_config(client: SonioxClient) -> None:
    route = _mock_tts_endpoint()

    client.tts.generate(
        text="hi", voice="Adrian", language="en", config=CreateTtsConfig(reduce_silence=True)
    )

    assert json.loads(route.calls.last.request.content)["reduce_silence"] is True


@respx.mock
def test_generate_omits_reduce_silence_when_unset(client: SonioxClient) -> None:
    """exclude_none keeps the field off the wire, so models without support are unaffected."""
    route = _mock_tts_endpoint()

    client.tts.generate(text="hi", voice="Adrian", language="en")

    assert "reduce_silence" not in json.loads(route.calls.last.request.content)


@respx.mock
def test_generate_without_language_warns_and_defaults_en(client: SonioxClient) -> None:
    """Omitting language is deprecated: warns now, still defaults to 'en' until next major."""
    route = _mock_tts_endpoint()

    with pytest.warns(DeprecationWarning, match="language"):
        client.tts.generate(text="hi", voice="Adrian")

    body = json.loads(route.calls.last.request.content)
    assert body["language"] == "en"


@respx.mock
def test_generate_deprecated_config_language_still_applies(client: SonioxClient) -> None:
    """language on the config warns but is honored; an explicit flat language wins over it."""
    route = _mock_tts_endpoint()

    with pytest.warns(DeprecationWarning, match="language"):
        client.tts.generate(text="hi", voice="Adrian", config=CreateTtsConfig(language="de"))
    assert json.loads(route.calls.last.request.content)["language"] == "de"

    with pytest.warns(DeprecationWarning, match="language"):
        client.tts.generate(
            text="hi", voice="Adrian", language="fr", config=CreateTtsConfig(language="de")
        )
    assert json.loads(route.calls.last.request.content)["language"] == "fr"


@respx.mock
def test_generate_overrides_via_config(client: SonioxClient) -> None:
    route = _mock_tts_endpoint()
    config = CreateTtsConfig(
        audio_format="mp3",
        sample_rate=24000,
        bitrate=128000,
    )

    client.tts.generate(
        text="hallo",
        voice="Adrian",
        model="custom-model",
        language="de",
        config=config,
    )

    body = json.loads(route.calls.last.request.content)
    assert body["model"] == "custom-model"
    assert body["language"] == "de"
    assert body["audio_format"] == "mp3"
    assert body["sample_rate"] == 24000
    assert body["bitrate"] == 128000


@respx.mock
def test_generate_deprecated_flat_kwargs_still_apply(client: SonioxClient) -> None:
    """The pre-move flat kwargs warn but keep working until the next major."""
    route = _mock_tts_endpoint()

    with pytest.warns(DeprecationWarning, match="CreateTtsConfig"):
        client.tts.generate(
            text="hi", voice="Adrian", language="en", audio_format="mp3", sample_rate=24000
        )

    body = json.loads(route.calls.last.request.content)
    assert body["audio_format"] == "mp3"
    assert body["sample_rate"] == 24000


@respx.mock
def test_generate_deprecated_config_model_and_voice_still_apply(client: SonioxClient) -> None:
    """model/voice set on the config warn but still override the call until the next major."""
    route = _mock_tts_endpoint()

    with pytest.warns(DeprecationWarning, match="model, voice"):
        client.tts.generate(
            text="hi",
            voice="flat-voice",
            model="flat-model",
            language="en",
            config=CreateTtsConfig(model="cfg-model", voice="cfg-voice"),
        )

    body = json.loads(route.calls.last.request.content)
    assert body["model"] == "cfg-model"
    assert body["voice"] == "cfg-voice"


@respx.mock
def test_generate_to_file_writes_path(client: SonioxClient, tmp_path: Path) -> None:
    _mock_tts_endpoint()
    out = tmp_path / "out.wav"

    written = client.tts.generate_to_file(out, text="hi", voice="Adrian", language="en")

    assert written == len(_AUDIO)
    assert out.read_bytes() == _AUDIO


@respx.mock
def test_generate_to_file_writes_str_path(client: SonioxClient, tmp_path: Path) -> None:
    _mock_tts_endpoint()
    out = tmp_path / "out.wav"

    written = client.tts.generate_to_file(str(out), text="hi", voice="Adrian", language="en")

    assert written == len(_AUDIO)
    assert out.read_bytes() == _AUDIO


@respx.mock
def test_generate_to_file_writes_binaryio(client: SonioxClient) -> None:
    _mock_tts_endpoint()
    buf = BytesIO()

    written = client.tts.generate_to_file(buf, text="hi", voice="Adrian", language="en")

    assert written == len(_AUDIO)
    assert buf.getvalue() == _AUDIO


@respx.mock
def test_generate_raises_on_api_error(client: SonioxClient) -> None:
    import pytest

    from soniox.errors import SonioxAPIError

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
        client.tts.generate(text="hi", voice="Adrian", language="en")
