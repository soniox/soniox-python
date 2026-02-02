from __future__ import annotations

import json
from enum import Enum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from .api import StructuredContext, TranslationConfig
from .common import Token


class RealtimeEvent(BaseModel):
    """Event payload received from the realtime STT websocket."""

    model_config = ConfigDict(extra="allow")

    tokens: list[Token] = Field(default=[])
    final_audio_proc_ms: int | None = None
    total_audio_proc_ms: int | None = None
    finished: bool = False
    error_code: int | None = None
    error_message: str | None = None

    @classmethod
    def validate_event(cls, raw: str | bytes) -> RealtimeEvent:
        payload = raw.decode("utf-8") if isinstance(raw, bytes | bytearray) else raw
        return cls.model_validate(json.loads(payload))


class RealtimeSttConfig(BaseModel):
    """Configuration for initiating a realtime transcription session."""

    api_key: str | None = None
    model: str
    audio_format: str = "auto"
    num_channels: int | None = None
    sample_rate: int | None = None
    language_hints: list[str] | None = None
    language_hints_strict: bool | None = None
    context: StructuredContext | None = None
    enable_speaker_diarization: bool | None = None
    enable_language_identification: bool | None = None
    enable_endpoint_detection: bool | None = None
    translation: TranslationConfig | None = None
    client_reference_id: str | None = None

    def build_payload(self, api_key: str) -> RealtimeSttConfig:
        return self.model_copy(update={"api_key": api_key})


class RealtimeControlType(str, Enum):
    """Control messages that can be sent over a realtime session."""

    FINISH = "finish"
    KEEP_ALIVE = "keep_alive"
    FINALIZE = "finalize"


EventType = Literal["open", "close", "finished", "error"]


class RealtimeSessionOpenPayload(BaseModel):
    """Event emitted when a realtime websocket session opens."""

    type: EventType = "open"
    model_config = ConfigDict(arbitrary_types_allowed=True)


class RealtimeSessionClosePayload(BaseModel):
    """Event emitted when a realtime websocket session closes."""

    type: EventType = "close"
    model_config = ConfigDict(arbitrary_types_allowed=True)


class RealtimeSessionFinishedPayload(BaseModel):
    """Event emitted when a realtime session finishes processing."""

    type: EventType = "finished"
    event: RealtimeEvent
    model_config = ConfigDict(arbitrary_types_allowed=True)


class RealtimeSessionErrorPayload(BaseModel):
    """Event emitted when a realtime session reports an error."""

    type: EventType = "error"
    error: Exception
    event: RealtimeEvent | None = None
    model_config = ConfigDict(arbitrary_types_allowed=True)


RealtimeSessionEventPayload = (
    RealtimeSessionOpenPayload
    | RealtimeSessionClosePayload
    | RealtimeSessionFinishedPayload
    | RealtimeSessionErrorPayload
)
