"""Shared constants and utilities for the Soniox SDK test suite."""

from __future__ import annotations

from typing import Any, TypeVar

from polyfactory.factories.pydantic_factory import ModelFactory
from pydantic import BaseModel

API_KEY = "test_key"
BASE_URL = "https://api.soniox.com/v1"

_M = TypeVar("_M", bound=BaseModel)


def build(model: type[_M]) -> _M:
    """Return a polyfactory-built instance of ``model``.

    Used in place of hand-written fixtures throughout the suite. Factories
    are created on demand (not declared upfront) so adding a new model
    never requires touching the tests.
    """
    factory_cls = type(f"{model.__name__}Factory", (ModelFactory,), {"__model__": model})
    return factory_cls.build()


def api_error_body(
    status: int,
    *,
    message: str = "boom",
    request_id: str = "req_1",
    validation_errors: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Build a realistic ``ApiError`` JSON payload for error-path testing."""
    body: dict[str, Any] = {
        "status_code": status,
        "error_type": "test_error",
        "message": message,
        "request_id": request_id,
    }
    if validation_errors is not None:
        body["validation_errors"] = validation_errors
    return body
