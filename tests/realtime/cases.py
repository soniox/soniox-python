"""
Realtime scenario table.

Each case describes: the session config, the server events to replay, and the
full sequence of messages the SDK is expected to send over the wire (including
the initial config handshake and the trailing FINISH sentinel).

The first element of ``expected_sent`` is always the config dict. ``b"..."``
entries are audio chunks the test driver will push with ``send_bytes``. The
final ``""`` is the FINISH control message emitted by ``session.finish()``.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from soniox.types.realtime import RealtimeSTTConfig


@dataclass
class RealtimeCase:
    id: str
    config: RealtimeSTTConfig
    server_events: list[dict[str, Any]]
    expected_sent: list[Any]
    # How many events the client should successfully consume from the server
    # before the session closes. Defaults to len(server_events).
    expected_received: int | None = None


def _config_dict(config: RealtimeSTTConfig, **extra: Any) -> dict[str, Any]:
    payload = config.model_dump(exclude_none=True)
    payload.setdefault("api_key", "test_key")
    payload.update(extra)
    return payload


_HAPPY_CONFIG = RealtimeSTTConfig(
    model="v1",
    audio_format="pcm_s16le",
    sample_rate=16000,
    num_channels=1,
)

_MIN_CONFIG = RealtimeSTTConfig(model="v1")


REALTIME_CASES: list[RealtimeCase] = [
    RealtimeCase(
        id="happy_path_simple",
        config=_HAPPY_CONFIG,
        server_events=[
            {"tokens": [{"text": "Hello", "is_final": True}]},
            {"tokens": [{"text": " world", "is_final": True}], "finished": True},
        ],
        expected_sent=[_config_dict(_HAPPY_CONFIG), b"audio-data", ""],
    ),
    RealtimeCase(
        id="multi_partial_then_final",
        config=_MIN_CONFIG,
        server_events=[
            {"tokens": [{"text": "Hel", "is_final": False}]},
            {"tokens": [{"text": "Hello", "is_final": False}]},
            {"tokens": [{"text": "Hello world", "is_final": True}]},
            {"tokens": [], "finished": True},
        ],
        expected_sent=[_config_dict(_MIN_CONFIG), b"chunk-1", b"chunk-2", ""],
    ),
    RealtimeCase(
        id="server_sends_error_event",
        config=_MIN_CONFIG,
        server_events=[
            {"tokens": [], "error_code": 400, "error_message": "Invalid audio format"},
        ],
        expected_sent=[_config_dict(_MIN_CONFIG), ""],
    ),
    RealtimeCase(
        id="finished_with_no_tokens",
        config=_MIN_CONFIG,
        server_events=[{"tokens": [], "finished": True}],
        expected_sent=[_config_dict(_MIN_CONFIG), ""],
    ),
]
