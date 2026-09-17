from __future__ import annotations

from typing import cast

import httpx
from pydantic import ValidationError

from .types import ApiError


class SonioxError(Exception):
    """Base exception for the SDK."""

    def __init__(self, message: str, *, response: httpx.Response | None = None) -> None:
        """
        Args:
            message: Description of what went wrong.
            response: HTTP response that caused the error, if any.
        """
        super().__init__(message)
        self.response: httpx.Response | None = response
        """HTTP response that caused the error, if any."""


class SonioxValidationError(SonioxError):
    """Raised when Pydantic input validation fails on the client side."""

    def __init__(self, message: str, *, errors: ValidationError | None = None) -> None:
        """
        Args:
            message: Description of what went wrong.
            errors: The underlying Pydantic validation error, if any.
        """
        super().__init__(message)
        self.errors: ValidationError | None = errors
        """The underlying Pydantic validation error, if any."""


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
        """
        Args:
            message: Description of what went wrong.
            api_error: Parsed error body; its ``error_type`` identifies the error.
            response: HTTP response that caused the error.
        """
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
        """
        Parse an `httpx.Response` into the matching SDK error.

        Args:
            response: Non-2xx HTTP response from the Soniox API.
        """
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
                    # WebSocket-style body, also used by TTS REST:
                    # {error_code, error_type, error_message, request_id, ...}
                    error_code = payload_dict.get("error_code")
                    error_type = payload_dict.get("error_type")
                    error_message = payload_dict.get("error_message")
                    request_id = payload_dict.get("request_id")
                    if isinstance(error_message, str):
                        status_code = (
                            int(error_code) if isinstance(error_code, int) else response.status_code
                        )
                        api_error = ApiError(
                            status_code=status_code,
                            error_type=error_type if isinstance(error_type, str) else "api_error",
                            message=error_message,
                            request_id=request_id if isinstance(request_id, str) else None,
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
        if api_error is not None and api_error.error_type == "permission_denied":
            error_cls = SonioxPermissionDeniedError
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


class SonioxPermissionDeniedError(SonioxAPIError):
    """
    The API key is valid but lacks the permission for this call (`403` with
    ``error_type`` ``permission_denied``). Other `403` errors, such as an expired
    temporary API key session, raise `SonioxAuthenticationError`. REST calls only;
    over WebSocket a permission error arrives as a realtime error event.

    See [API key permissions](https://soniox.com/docs/guides/api-key-permissions).
    """


class SonioxInvalidRequestError(SonioxAPIError):
    """Invalid request payloads (`400`)."""


class SonioxNotFoundError(SonioxAPIError):
    """Resource not found (`404`)."""


class SonioxConflictError(SonioxAPIError):
    """Conflict or invalid state, e.g. deleting while processing (`409`)."""


class SonioxRateLimitError(SonioxAPIError):
    """Rate limit or usage limit exceeded (`429`)."""


class SonioxServerError(SonioxAPIError):
    """Server errors (`5xx`)."""


class InvalidWebhookSignatureError(SonioxError):
    """Raised when a webhook signature cannot be validated."""


class SonioxRealtimeError(SonioxError):
    """Errors raised by realtime workflows."""
