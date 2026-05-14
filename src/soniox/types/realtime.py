from __future__ import annotations

import json
from base64 import b64decode
from enum import Enum
from typing import get_args

from pydantic import BaseModel, ConfigDict, Field, model_validator
from typing_extensions import Self

from .api import (
    RealtimeSTTAudioFormat,
    RealtimeSTTRawFormat,
    StructuredContextInput,
    TranslationConfigInput,
    TtsAudioFormat,
    TtsBitrate,
    TtsSampleRate,
)
from .common import Token

_RAW_FORMAT_VALUES = set(get_args(RealtimeSTTRawFormat))


class RealtimeEvent(BaseModel):
    """Event payload received from the realtime STT websocket."""

    model_config = ConfigDict(extra="allow")

    tokens: list[Token] = Field(default=[])
    """Tokens in this result."""

    final_audio_proc_ms: int | None = None
    """Milliseconds of audio that have been finalized."""

    total_audio_proc_ms: int | None = None
    """Total milliseconds of audio processed."""

    finished: bool = False
    """Whether this is the final result (session ending)."""

    error_code: int | None = None
    """Error code if the realtime operation failed."""

    error_message: str | None = None
    """Human-readable description of the error."""

    @classmethod
    def validate_event(cls, raw: str | bytes) -> RealtimeEvent:
        payload = raw.decode("utf-8") if isinstance(raw, bytes | bytearray) else raw
        return cls.model_validate(json.loads(payload))


class RealtimeSTTConfig(BaseModel):
    """Configuration for initiating a realtime transcription session."""

    api_key: str | None = None
    """API key for real-time sessions."""

    model: str
    """Speech-to-text model to use."""

    audio_format: RealtimeSTTAudioFormat = "auto"
    """Audio format. Use 'auto' for automatic detection of container formats."""

    num_channels: int | None = None
    """Number of audio channels (required for raw audio formats)."""

    sample_rate: int | None = None
    """Sample rate in Hz (required for PCM formats)."""

    language_hints: list[str] | None = None
    """Expected languages in the audio (ISO language codes)."""

    language_hints_strict: bool | None = None
    """When true, recognition is strongly biased toward language hints (best results when using one language in language_hints)."""

    context: StructuredContextInput | None = None
    """Additional context to improve transcription accuracy."""

    enable_speaker_diarization: bool | None = None
    """Enable speaker identification."""

    enable_language_identification: bool | None = None
    """Enable automatic language detection."""

    enable_endpoint_detection: bool | None = None
    """Enable endpoint detection for utterance boundaries."""

    max_endpoint_delay_ms: int | None = Field(default=None, ge=500, le=3000)
    """
    Maximum delay between the end of speech and returned endpoint.
    Allowed values for maximum delay are between 500ms and 3000ms. The default value is 2000ms
    """

    translation: TranslationConfigInput | None = None
    """Translation configuration."""

    client_reference_id: str | None = Field(default=None, max_length=256)
    """Optional tracking identifier (max 256 chars)."""

    @model_validator(mode="after")
    def _raw_formats_require_rate_and_channels(self) -> Self:
        if self.audio_format not in _RAW_FORMAT_VALUES:
            return self
        missing: list[str] = []
        if self.sample_rate is None:
            missing.append("sample_rate")
        if self.num_channels is None:
            missing.append("num_channels")
        if missing:
            raise ValueError(
                f"audio_format={self.audio_format!r} has no header and requires "
                f"{' and '.join(missing)} to be set explicitly"
            )
        return self

    def build_payload(self, api_key: str) -> RealtimeSTTConfig:
        return self.model_copy(update={"api_key": api_key})


class RealtimeTTSConfig(BaseModel):
    """Configuration for initiating a realtime Text-to-Speech stream."""

    api_key: str | None = None
    """API key for real-time sessions."""

    stream_id: str = Field(min_length=1, max_length=256)
    """Client stream identifier unique among active streams on a connection."""

    model: str = Field(min_length=1, max_length=50)
    """Text-to-Speech model to use."""

    language: str = Field(min_length=1, max_length=50)
    """Language code for Text-to-Speech (e.g., "en")."""

    voice: str = Field(min_length=1, max_length=50)
    """Voice identifier to generate speech audio with."""

    audio_format: TtsAudioFormat
    """Requested output audio format."""

    sample_rate: TtsSampleRate | None = Field(default=None)
    """Output sample rate in Hz."""

    bitrate: TtsBitrate | None = Field(default=None)
    """Output bitrate in bits-per-second for compressed formats."""

    def build_payload(self, api_key: str) -> RealtimeTTSConfig:
        return self.model_copy(update={"api_key": api_key})


class RealtimeTTSTextMessage(BaseModel):
    """Text chunk message sent over realtime Text-to-Speech websocket."""

    text: str = Field(default="", max_length=5000)
    """Text chunk to generate into speech."""

    text_end: bool = False
    """Whether this message marks the final text chunk for the stream."""

    stream_id: str = Field(min_length=1, max_length=256)
    """Stream identifier the chunk belongs to."""


class RealtimeTTSCancelMessage(BaseModel):
    """Cancel a realtime Text-to-Speech stream."""

    stream_id: str = Field(min_length=1, max_length=256)
    """Stream identifier to cancel."""

    cancel: bool = True
    """Whether to cancel the stream."""


class RealtimeTTSKeepAliveMessage(BaseModel):
    """Keepalive message for realtime Text-to-Speech websocket sessions."""

    keep_alive: bool = True
    """Whether to send a keepalive control message."""


class RealtimeTTSEvent(BaseModel):
    """Event payload received from the realtime Text-to-Speech websocket."""

    model_config = ConfigDict(extra="allow")

    stream_id: str | None = None
    """Stream identifier associated with this event."""

    audio: str | None = None
    """Base64 encoded audio chunk, when present."""

    audio_end: bool = False
    """Whether this event contains the last audio payload for the stream."""

    terminated: bool = False
    """Whether the stream has been fully terminated."""

    error_code: int | None = None
    """Error code if the Text-to-Speech stream failed."""

    error_message: str | None = None
    """Human-readable error message."""

    @classmethod
    def validate_event(cls, raw: str | bytes) -> RealtimeTTSEvent:
        payload = raw.decode("utf-8") if isinstance(raw, bytes | bytearray) else raw
        return cls.model_validate(json.loads(payload))

    def audio_bytes(self) -> bytes | None:
        """Decode and return the audio bytes for this event, if present."""
        if self.audio is None:
            return None
        try:
            return b64decode(self.audio, validate=True)
        except ValueError as exc:
            raise ValueError(
                "Invalid base64 audio payload in realtime Text-to-Speech event"
            ) from exc


class RealtimeControlType(str, Enum):
    """Control messages that can be sent over a realtime session."""

    FINISH = "finish"
    KEEP_ALIVE = "keep_alive"
    FINALIZE = "finalize"


# Protocol Constants
TOKEN_TEXT_FIN = "<fin>"
TOKEN_TEXT_END = "<end>"
