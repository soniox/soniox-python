from __future__ import annotations

import httpx
from pydantic import ValidationError

from .types import ApiError


class SonioxError(Exception):
    """Base exception for the SDK."""

    def __init__(self, message: str, *, response: httpx.Response | None = None) -> None:
        super().__init__(message)
        self.response = response


class SonioxValidationError(SonioxError):
    """Raised when Pydantic input validation fails on the client side."""

    def __init__(self, message: str, *, errors: ValidationError | None = None) -> None:
        super().__init__(message)
        self.errors = errors


class SonioxAPIError(SonioxError):
    """Raised when the Soniox API replies with a non-2xx payload."""

    api_error: ApiError | None
    status_code: int | None
    request_id: str | None

    def __init__(
        self,
        message: str,
        *,
        api_error: ApiError | None = None,
        response: httpx.Response | None = None,
    ) -> None:
        super().__init__(message, response=response)
        self.api_error = api_error
        self.status_code = response.status_code if response is not None else None
        self.request_id = api_error.request_id if api_error is not None else None

    def __str__(self) -> str:
        base = self.api_error.message if self.api_error else super().__str__()
        status = f" (HTTP {self.status_code})" if self.status_code else ""
        return f"{base}{status}"

    @classmethod
    def from_response(cls, response: httpx.Response) -> SonioxAPIError:
        try:
            payload = response.json()
        except ValueError as exc:
            raise SonioxAPIError(
                "Unable to decode error response payload", response=response
            ) from exc

        try:
            api_error = ApiError.model_validate(payload)
        except ValidationError as exc:
            raise SonioxAPIError("Unable to parse API error schema", response=response) from exc

        error_cls = cls._map_status_to_exception(response.status_code)
        return error_cls(api_error.message, api_error=api_error, response=response)

    @classmethod
    def _map_status_to_exception(cls, status_code: int) -> type[SonioxAPIError]:
        if status_code == 400:
            return SonioxInvalidRequestError
        if status_code in (401, 403):
            return SonioxAuthenticationError
        if status_code == 404:
            return SonioxNotFoundError
        if status_code == 409:
            return SonioxConflictError
        if status_code == 429:
            return SonioxRateLimitError
        if status_code >= 500:
            return SonioxServerError
        return SonioxAPIError


class SonioxAuthenticationError(SonioxAPIError):
    """Authentication failures (`401`/`403`)."""


class SonioxInvalidRequestError(SonioxAPIError):
    """Invalid request payloads (`400`)."""


class SonioxNotFoundError(SonioxAPIError):
    """Resource not found."""


class SonioxConflictError(SonioxAPIError):
    """Conflict or invalid state (e.g., delete while processing)."""


class SonioxRateLimitError(SonioxAPIError):
    """Rate limit (429)."""


class SonioxServerError(SonioxAPIError):
    """5xx responses."""


class InvalidWebhookSignatureError(SonioxError):
    """Raised when a webhook signature cannot be validated."""
