"""
Mapping from OpenAPI ``operationId`` to the matching SDK call shape.

OpenAPI tells us the wire contract (method, URL, status, response model).
It does *not* tell us how to invoke the SDK - that's a Python-side concern.
This file fills that gap and nothing else.

Two maps:

* :data:`SDK_BINDINGS` - one entry per operation, calling the SDK with the
  *minimum* required arguments. The coverage guard in ``test_api.py``
  enforces that every schema operation is represented here.
* :data:`SDK_BINDINGS_FULL` - optional overrides that call the same endpoint
  with *every* optional field populated. Used to catch "SDK silently drops a
  newly-added optional field" regressions. Only operations that *have*
  meaningful optional fields appear here.

The happy-path tests parametrize over the union, so every endpoint gets
tested at the min surface and (where applicable) the full surface.
"""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from io import BytesIO
from typing import Any

from soniox.client import AsyncSonioxClient, SonioxClient
from soniox.types import CreateTranscriptionConfig

from ._openapi import PATH_PARAM_VALUE

SyncCall = Callable[[SonioxClient], Any]
AsyncCall = Callable[[AsyncSonioxClient], Awaitable[Any]]


@dataclass(frozen=True)
class SdkBinding:
    """How to invoke the SDK for a given OpenAPI operation."""

    sync_call: SyncCall
    async_call: AsyncCall
    expect_params: dict[str, str] = field(default_factory=dict)
    expect_json: dict[str, Any] = field(default_factory=dict)
    expect_multipart: bool = False


_ID = PATH_PARAM_VALUE  # "abc-123"
_AUDIO_URL = "https://example.com/audio.mp3"

# ---------------------------------------------------------------------------
# Minimum-argument bindings - one entry per operation (coverage guard).
# ---------------------------------------------------------------------------

SDK_BINDINGS: dict[str, SdkBinding] = {
    "get_files": SdkBinding(
        sync_call=lambda c: c.files.list(limit=5),
        async_call=lambda c: c.files.list(limit=5),
        expect_params={"limit": "5"},
    ),
    "get_files_count": SdkBinding(
        sync_call=lambda c: c.files.count(),
        async_call=lambda c: c.files.count(),
    ),
    "upload_file": SdkBinding(
        sync_call=lambda c: c.files.upload(BytesIO(b"audio-bytes"), filename="clip.mp3"),
        async_call=lambda c: c.files.upload(BytesIO(b"audio-bytes"), filename="clip.mp3"),
        expect_multipart=True,
    ),
    "get_file": SdkBinding(
        sync_call=lambda c: c.files.get(_ID),
        async_call=lambda c: c.files.get(_ID),
    ),
    "delete_file": SdkBinding(
        sync_call=lambda c: c.files.delete(_ID),
        async_call=lambda c: c.files.delete(_ID),
    ),
    "get_transcriptions": SdkBinding(
        sync_call=lambda c: c.stt.list(limit=5),
        async_call=lambda c: c.stt.list(limit=5),
        expect_params={"limit": "5"},
    ),
    "get_transcriptions_count": SdkBinding(
        sync_call=lambda c: c.stt.count(),
        async_call=lambda c: c.stt.count(),
    ),
    "create_transcription": SdkBinding(
        sync_call=lambda c: c.stt.create(model="stt-async-v4", audio_url=_AUDIO_URL),
        async_call=lambda c: c.stt.create(model="stt-async-v4", audio_url=_AUDIO_URL),
        expect_json={"model": "stt-async-v4", "audio_url": _AUDIO_URL},
    ),
    "get_transcription": SdkBinding(
        sync_call=lambda c: c.stt.get(_ID),
        async_call=lambda c: c.stt.get(_ID),
    ),
    "delete_transcription": SdkBinding(
        sync_call=lambda c: c.stt.delete(_ID),
        async_call=lambda c: c.stt.delete(_ID),
    ),
    "get_transcription_transcript": SdkBinding(
        sync_call=lambda c: c.stt.get_transcript(_ID),
        async_call=lambda c: c.stt.get_transcript(_ID),
    ),
    "get_models": SdkBinding(
        sync_call=lambda c: c.models.list(),
        async_call=lambda c: c.models.list(),
    ),
    "get_tts_models": SdkBinding(
        sync_call=lambda c: c.tts_models.list(),
        async_call=lambda c: c.tts_models.list(),
    ),
    "get_usage_logs": SdkBinding(
        sync_call=lambda c: c.usage_logs.list(
            start_time="2026-01-01T00:00:00Z", end_time="2026-02-01T00:00:00Z"
        ),
        async_call=lambda c: c.usage_logs.list(
            start_time="2026-01-01T00:00:00Z", end_time="2026-02-01T00:00:00Z"
        ),
    ),
    "get_concurrency_limits": SdkBinding(
        sync_call=lambda c: c.concurrency_limits.get(),
        async_call=lambda c: c.concurrency_limits.get(),
    ),
    "create_temporary_api_key": SdkBinding(
        sync_call=lambda c: c.auth.create_temporary_api_key(usage_type="transcribe_websocket"),
        async_call=lambda c: c.auth.create_temporary_api_key(usage_type="transcribe_websocket"),
        expect_json={"usage_type": "transcribe_websocket"},
    ),
}


# ---------------------------------------------------------------------------
# Full-surface bindings - every optional field populated.
# ---------------------------------------------------------------------------

_FULL_CONFIG = CreateTranscriptionConfig(
    language_hints=["en", "de"],
    language_hints_strict=True,
    enable_speaker_diarization=True,
    enable_language_identification=True,
    client_reference_id="ref-123",
)

SDK_BINDINGS_FULL: dict[str, SdkBinding] = {
    "get_files": SdkBinding(
        sync_call=lambda c: c.files.list(limit=10, cursor="page-token"),
        async_call=lambda c: c.files.list(limit=10, cursor="page-token"),
        expect_params={"limit": "10", "cursor": "page-token"},
    ),
    "upload_file": SdkBinding(
        sync_call=lambda c: c.files.upload(
            BytesIO(b"audio-bytes"),
            filename="clip.mp3",
            client_reference_id="ref-123",
        ),
        async_call=lambda c: c.files.upload(
            BytesIO(b"audio-bytes"),
            filename="clip.mp3",
            client_reference_id="ref-123",
        ),
        expect_multipart=True,
    ),
    "get_transcriptions": SdkBinding(
        sync_call=lambda c: c.stt.list(limit=10, cursor="page-token"),
        async_call=lambda c: c.stt.list(limit=10, cursor="page-token"),
        expect_params={"limit": "10", "cursor": "page-token"},
    ),
    "create_transcription": SdkBinding(
        sync_call=lambda c: c.stt.create(
            model="stt-async-v4",
            audio_url=_AUDIO_URL,
            client_reference_id="ref-123",
            config=_FULL_CONFIG,
        ),
        async_call=lambda c: c.stt.create(
            model="stt-async-v4",
            audio_url=_AUDIO_URL,
            client_reference_id="ref-123",
            config=_FULL_CONFIG,
        ),
        expect_json={
            "model": "stt-async-v4",
            "audio_url": _AUDIO_URL,
            "client_reference_id": "ref-123",
            "language_hints": ["en", "de"],
            "language_hints_strict": True,
            "enable_speaker_diarization": True,
            "enable_language_identification": True,
        },
    ),
    "create_temporary_api_key": SdkBinding(
        sync_call=lambda c: c.auth.create_temporary_api_key(
            usage_type="transcribe_websocket",
            expires_in_seconds=1200,
            max_session_duration_seconds=900,
            single_use=True,
            client_reference_id="ref-123",
        ),
        async_call=lambda c: c.auth.create_temporary_api_key(
            usage_type="transcribe_websocket",
            expires_in_seconds=1200,
            max_session_duration_seconds=900,
            single_use=True,
            client_reference_id="ref-123",
        ),
        expect_json={
            "usage_type": "transcribe_websocket",
            "expires_in_seconds": 1200,
            "max_session_duration_seconds": 900,
            "single_use": True,
            "client_reference_id": "ref-123",
        },
    ),
}
