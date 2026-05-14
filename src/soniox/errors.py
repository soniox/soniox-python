from __future__ import annotations

from typing import cast

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
        validation = ""
        if self.api_error and self.api_error.validation_errors:
            validation_errors = ", ".join(
                f"{err.location}: {err.message}" for err in self.api_error.validation_errors
            )
            validation = f" Validation errors: {validation_errors}"
        return f"{base}{status}{validation}"

    @classmethod
    def from_response(cls, response: httpx.Response) -> SonioxAPIError:
        """Parse an `httpx.Response` into a richer SDK error."""
        api_error: ApiError | None = None
        payload = None
        try:
            payload = response.json()
        except ValueError:
            pass
        if payload is not None:
            try:
                api_error = ApiError.model_validate(payload)
            except ValidationError as exc:
                if isinstance(payload, dict):
                    payload_dict = cast("dict[str, object]", payload)
                    error_code = payload_dict.get("error_code")
                    error_message = payload_dict.get("error_message")
                    if isinstance(error_message, str):
                        status_code = (
                            int(error_code) if isinstance(error_code, int) else response.status_code
                        )
                        api_error = ApiError(
                            status_code=status_code,
                            error_type="api_error",
                            message=error_message,
                        )
                    else:
                        raise SonioxAPIError(
                            "Unable to parse API error schema", response=response
                        ) from exc
                else:
                    raise SonioxAPIError(
                        "Unable to parse API error schema", response=response
                    ) from exc
        error_cls = cls._map_status_to_exception(response.status_code)
        if api_error:
            message = api_error.message
        else:
            text = (response.text or "").strip()
            if text.lower().startswith("<!doctype") or text.startswith("<html"):
                message = response.reason_phrase
            else:
                message = text or response.reason_phrase
        return error_cls(message, api_error=api_error, response=response)

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


class SonioxRealtimeError(SonioxError):
    """Errors raised by realtime workflows."""
