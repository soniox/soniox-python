from __future__ import annotations

from typing import TypeVar

import httpx
from pydantic import BaseModel

ModelT = TypeVar("ModelT", bound=BaseModel)


def parse_response(response: httpx.Response, model: type[ModelT]) -> ModelT:
    response.raise_for_status()
    payload = response.json()
    return model.model_validate(payload)


async def parse_async_response(response: httpx.Response, model: type[ModelT]) -> ModelT:
    response.raise_for_status()
    payload = response.json()
    return model.model_validate(payload)
