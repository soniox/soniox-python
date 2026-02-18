from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class Token(BaseModel):
    """Token metadata emitted during realtime streaming transcriptions."""

    model_config = ConfigDict(extra="allow")

    text: str
    """The transcribed text."""

    start_ms: int | None = None
    """Start time in milliseconds relative to audio start."""

    end_ms: int | None = None
    """End time in milliseconds relative to audio start."""

    confidence: float | None = None
    """Confidence score (0.0 to 1.0)."""

    is_final: bool | None = None
    """Whether this is a finalized token."""

    speaker: str | None = None
    """Speaker identifier (if diarization enabled)."""

    translation_status: str | None = None
    """Translation status of this token."""

    language: str | None = None
    """Detected language code (if language identification enabled)."""

    source_language: str | None = None
    """Source language for translated tokens."""
