from __future__ import annotations

import json
from collections.abc import Callable, Mapping
from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict

from .api import StructuredContext, TranslationConfig


class RealtimeToken(BaseModel):
    model_config = ConfigDict(extra="allow")

    text: str
    start_ms: int | None = None
    end_ms: int | None = None
    confidence: float | None = None
    is_final: bool | None = None
    speaker: str | None = None
    translation_status: str | None = None
    language: str | None = None
    source_language: str | None = None


class RealtimeEvent(BaseModel):
    model_config = ConfigDict(extra="allow")

    tokens: list[RealtimeToken] = []
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
    model: str
    audio_format: str = "auto"
    num_channels: int | None = None
    sample_rate: int | None = None
    language_hints: list[str] | None = None
    language_hints_strict: bool | None = None
    context: StructuredContext | Mapping[str, Any] | None = None
    enable_speaker_diarization: bool | None = None
    enable_language_identification: bool | None = None
    enable_endpoint_detection: bool | None = None
    translation: TranslationConfig | None = None
    client_reference_id: str | None = None

    def build_payload(self, api_key: str) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "api_key": api_key,
            "model": self.model,
            "audio_format": self.audio_format,
        }
        if self.num_channels is not None:
            payload["num_channels"] = self.num_channels
        if self.sample_rate is not None:
            payload["sample_rate"] = self.sample_rate
        if self.language_hints is not None:
            payload["language_hints"] = self.language_hints
        if self.language_hints_strict is not None:
            payload["language_hints_strict"] = self.language_hints_strict
        if self.context is not None:
            if isinstance(self.context, StructuredContext):
                payload["context"] = self.context.model_dump(exclude_none=True)
            else:
                payload["context"] = dict(self.context)
        if self.enable_speaker_diarization is not None:
            payload["enable_speaker_diarization"] = self.enable_speaker_diarization
        if self.enable_language_identification is not None:
            payload["enable_language_identification"] = self.enable_language_identification
        if self.enable_endpoint_detection is not None:
            payload["enable_endpoint_detection"] = self.enable_endpoint_detection
        if self.translation is not None:
            payload["translation"] = self.translation.model_dump(exclude_none=True)
        if self.client_reference_id is not None:
            payload["client_reference_id"] = self.client_reference_id
        return payload


class RealtimeSessionEvent(Enum):
    OPEN = "open"
    CLOSE = "close"
    MESSAGE = "message"
    ERROR = "error"


class RealtimeControlType(str, Enum):
    FINISH = "finish"
    KEEP_ALIVE = "keep_alive"
    FINALIZE = "finalize"


RealtimeEventCallback = Callable[[RealtimeEvent], None]
RealtimeSessionCallback = Callable[[RealtimeSessionEvent, Any], None]
RealtimeErrorCallback = Callable[[Exception, Any], None]
