from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class Token(BaseModel):
    model_config = ConfigDict(extra="allow")

    text: str
    start_ms: float | None = None
    end_ms: float | None = None
    confidence: float | None = None
    is_final: bool | None = None
    speaker: str | None = None
    translation_status: str | None = None
    language: str | None = None
    source_language: str | None = None
