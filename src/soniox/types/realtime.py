from __future__ import annotations

import json
from collections.abc import Callable
from enum import Enum

from pydantic import BaseModel, ConfigDict

from .api import StructuredContext, TranslationConfig
from .common import Token


class RealtimeEvent(BaseModel):
    model_config = ConfigDict(extra="allow")

    tokens: list[Token] = []
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
