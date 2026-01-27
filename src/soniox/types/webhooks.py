from __future__ import annotations

from collections.abc import Mapping
from typing import Literal, TypeAlias

from pydantic import BaseModel, Field


class WebhookAuthConfig(BaseModel):
    name: str
    value: str


class WebhookEvent(BaseModel):
    id: str = Field(min_length=1)
    status: Literal["completed", "error"]


Headers: TypeAlias = Mapping[str, str]
