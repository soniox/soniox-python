from __future__ import annotations

import httpx
from pydantic import ValidationError

from .types import ApiError


class SonioxError(Exception):
    """Base class for every SDK-level error."""

    def __init__(self, message: str, *, response: httpx.Response | None = None) -> None:
        super().__init__(message)
        self.response = response


class ApiErrorException(SonioxError):
    """Raised when the Soniox API returns an error payload."""

    def __init__(self, api_error: ApiError, *, response: httpx.Response) -> None:
        super().__init__(api_error.message, response=response)
        self.api_error = api_error

    def __str__(self) -> str:
        return (
            f"{self.api_error.error_type} ({self.api_error.status_code}): {self.api_error.message}"
        )

    @classmethod
    def from_response(cls, response: httpx.Response) -> ApiErrorException:
        try:
            payload = response.json()
        except ValueError as exc:
            raise SonioxError("Invalid JSON in error response", response=response) from exc

        try:
            api_error = ApiError.model_validate(payload)
        except ValidationError as exc:
            raise SonioxError("Unable to deserialize API error payload", response=response) from exc

        return cls(api_error, response=response)
