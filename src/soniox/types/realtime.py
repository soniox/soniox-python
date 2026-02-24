from __future__ import annotations

import json
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field

from .api import StructuredContext, TranslationConfig
from .common import Token


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

    audio_format: str = "auto"
    """Audio format. Use 'auto' for automatic detection of container formats."""

    num_channels: int | None = None
    """Number of audio channels (required for raw audio formats)."""

    sample_rate: int | None = None
    """Sample rate in Hz (required for PCM formats)."""

    language_hints: list[str] | None = None
    """Expected languages in the audio (ISO language codes)."""

    language_hints_strict: bool | None = None
    """When true, recognition is strongly biased toward language hints (best results when using one language in language_hints)."""

    context: StructuredContext | None = None
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

    translation: TranslationConfig | None = None
    """Translation configuration."""

    client_reference_id: str | None = Field(default=None, max_length=256)
    """Optional tracking identifier (max 256 chars)."""

    def build_payload(self, api_key: str) -> RealtimeSTTConfig:
        return self.model_copy(update={"api_key": api_key})


class RealtimeControlType(str, Enum):
    """Control messages that can be sent over a realtime session."""

    FINISH = "finish"
    KEEP_ALIVE = "keep_alive"
    FINALIZE = "finalize"


# Protocol Constants
TOKEN_TEXT_FIN = "<fin>"
TOKEN_TEXT_END = "<end>"
