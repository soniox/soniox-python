"""Tests for type validators and input coercion in soniox.types."""

from __future__ import annotations

import json

import pytest

from soniox.types import (
    CreateTtsConfig,
    RealtimeSTTConfig,
    RealtimeTTSConfig,
    RealtimeTTSEvent,
    StructuredContext,
    StructuredContextGeneralItem,
    StructuredContextTranslationTerm,
)


# ---------------------------------------------------------------------------
# StructuredContext dict-input coercion
# ---------------------------------------------------------------------------


def test_structured_context_general_accepts_dict() -> None:
    ctx = StructuredContext(general={"domain": "Healthcare", "topic": "Radiology"})
    assert ctx.general == [
        StructuredContextGeneralItem(key="domain", value="Healthcare"),
        StructuredContextGeneralItem(key="topic", value="Radiology"),
    ]


def test_structured_context_translation_terms_accepts_dict() -> None:
    ctx = StructuredContext(translation_terms={"Mr. Smith": "Sr. Smith"})
    assert ctx.translation_terms == [
        StructuredContextTranslationTerm(source="Mr. Smith", target="Sr. Smith"),
    ]


def test_structured_context_general_keeps_typed_list_unchanged() -> None:
    items = [StructuredContextGeneralItem(key="domain", value="Healthcare")]
    ctx = StructuredContext(general=items)
    assert ctx.general == items


# ---------------------------------------------------------------------------
# RealtimeSTTConfig raw-format validation
# ---------------------------------------------------------------------------


def test_raw_format_requires_sample_rate_and_channels() -> None:
    with pytest.raises(ValueError) as exc:
        RealtimeSTTConfig(model="stt-rt-mock", audio_format="pcm_s16le")
    msg = str(exc.value)
    assert "sample_rate" in msg
    assert "num_channels" in msg


def test_raw_format_requires_sample_rate_only() -> None:
    with pytest.raises(ValueError) as exc:
        RealtimeSTTConfig(model="stt-rt-mock", audio_format="pcm_s16le", num_channels=1)
    assert "sample_rate" in str(exc.value)


def test_raw_format_requires_num_channels_only() -> None:
    with pytest.raises(ValueError) as exc:
        RealtimeSTTConfig(model="stt-rt-mock", audio_format="pcm_s16le", sample_rate=16000)
    assert "num_channels" in str(exc.value)


def test_raw_format_with_both_succeeds() -> None:
    cfg = RealtimeSTTConfig(model="stt-rt-mock", audio_format="pcm_s16le", sample_rate=16000, num_channels=1)
    assert cfg.audio_format == "pcm_s16le"
    assert cfg.sample_rate == 16000
    assert cfg.num_channels == 1


def test_endpoint_latency_adjustment_level_accepts_0_to_3() -> None:
    for level in (0, 3):
        cfg = RealtimeSTTConfig(model="stt-rt-mock", endpoint_latency_adjustment_level=level)
        assert cfg.endpoint_latency_adjustment_level == level


def test_endpoint_latency_adjustment_level_rejects_out_of_range() -> None:
    with pytest.raises(ValueError):
        RealtimeSTTConfig(model="stt-rt-mock", endpoint_latency_adjustment_level=4)


# ---------------------------------------------------------------------------
# TTS speed bounds (0.7-1.3) and timestamps
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("speed", [0.7, 1.0, 1.3])
def test_tts_speed_accepts_in_range(speed: float) -> None:
    assert CreateTtsConfig(speed=speed).speed == speed
    assert RealtimeTTSConfig(stream_id="s", model="tts-rt-mock", language="en", voice="Adrian",
                             audio_format="wav", speed=speed).speed == speed


@pytest.mark.parametrize("speed", [0.6, 1.4])
def test_tts_speed_rejects_out_of_range(speed: float) -> None:
    with pytest.raises(ValueError):
        CreateTtsConfig(speed=speed)


def test_realtime_tts_event_parses_timestamps() -> None:
    raw = json.dumps({
        "stream_id": "s",
        "audio": "AAAA",
        "timestamps": {
            "characters": ["H", "i"],
            "character_start_times_seconds": [0.0, 0.1],
            "character_end_times_seconds": [0.1, 0.25],
        },
    })
    event = RealtimeTTSEvent.validate_event(raw)
    assert event.timestamps is not None
    assert event.timestamps.characters == ["H", "i"]
    assert event.timestamps.character_end_times_seconds == [0.1, 0.25]


def test_realtime_tts_event_without_timestamps_is_none() -> None:
    event = RealtimeTTSEvent.validate_event(json.dumps({"stream_id": "s", "audio": "AAAA"}))
    assert event.timestamps is None


def test_endpoints_come_from_the_environment_when_not_passed(monkeypatch):
    """A deployment can be selected without touching code."""
    from soniox.client import SonioxClient

    monkeypatch.setenv("SONIOX_API_KEY", "env-key")
    monkeypatch.setenv("SONIOX_API_BASE_URL", "https://api.example.com/v1")
    monkeypatch.setenv("SONIOX_WS_URL", "wss://stt.example.com/transcribe-websocket")
    monkeypatch.setenv("SONIOX_TTS_API_URL", "https://tts.example.com")
    monkeypatch.setenv("SONIOX_TTS_WS_URL", "wss://tts.example.com/tts-websocket")

    client = SonioxClient()

    assert client.api_key == "env-key"
    assert client.api_base_url == "https://api.example.com/v1"
    assert client.websocket_base_url == "wss://stt.example.com/transcribe-websocket"
    assert client.tts_api_base_url == "https://tts.example.com"
    assert client.tts_websocket_base_url == "wss://tts.example.com/tts-websocket"


def test_endpoint_arguments_win_over_the_environment(monkeypatch):
    from soniox.client import SonioxClient

    monkeypatch.setenv("SONIOX_API_BASE_URL", "https://env.example.com/v1")

    client = SonioxClient(api_key="k", api_base_url="https://arg.example.com/v1")

    assert client.api_base_url == "https://arg.example.com/v1"
