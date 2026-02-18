from __future__ import annotations

from collections.abc import Mapping
from typing import Literal, TypeAlias

from pydantic import BaseModel, Field


class WebhookAuthConfig(BaseModel):
    """Configuration for webhook authentication headers."""

    name: str
    """Expected header name (case-insensitive comparison)."""

    value: str
    """Expected header value (exact match)."""


class WebhookEvent(BaseModel):
    """Basic webhook event metadata."""

    id: str = Field(min_length=1)
    """Transcription ID (UUID)."""

    status: Literal["completed", "error"]
    """Transcription result status."""


Headers: TypeAlias = Mapping[str, str]
