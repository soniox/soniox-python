from __future__ import annotations

import json
import os

from ..errors import InvalidWebhookSignatureError
from ..types import Headers, WebhookAuthConfig, WebhookEvent

SONIOX_API_WEBHOOK_HEADER_ENV = "SONIOX_API_WEBHOOK_HEADER"
SONIOX_API_WEBHOOK_SECRET_ENV = "SONIOX_API_WEBHOOK_SECRET"
DEFAULT_WEBHOOK_HEADER = "X-Soniox-Webhook-Secret"


def _get_header_value(headers: Headers, name: str) -> str | None:
    value = headers.get(name)
    if value is not None:
        return value
    lower_name = name.lower()
    for key, val in headers.items():
        if key.lower() == lower_name:
            return val
    return None


def _resolve_webhook_auth(
    header: str | None,
    secret: str | None,
) -> WebhookAuthConfig | None:
    header_name = header or os.getenv(SONIOX_API_WEBHOOK_HEADER_ENV) or DEFAULT_WEBHOOK_HEADER
    header_value = secret or os.getenv(SONIOX_API_WEBHOOK_SECRET_ENV)
    if not header_name or not header_value:
        return None
    return WebhookAuthConfig(name=header_name, value=header_value)


class SonioxWebhooksAPI:
    def __init__(
        self,
        *,
        webhook_secret: str | None = None,
        webhook_header: str | None = None,
    ) -> None:
        self._webhook_secret = webhook_secret
        self._webhook_header = webhook_header

    def verify_signature(
        self,
        headers: Headers,
        *,
        auth: WebhookAuthConfig | None = None,
    ) -> None:
        """
        Verify a webhook signature from headers.

        Raises:
            InvalidWebhookSignatureError: When the webhook signature cannot be validated.
        """
        auth_config = auth or _resolve_webhook_auth(
            self._webhook_header,
            self._webhook_secret,
        )
        if auth_config is None:
            return

        header_value = _get_header_value(headers, auth_config.name)

        if header_value != auth_config.value:
            raise InvalidWebhookSignatureError("Invalid webhook signature")

    def unwrap(
        self,
        payload: str | bytes,
        headers: Headers,
        *,
        auth: WebhookAuthConfig | None = None,
    ) -> WebhookEvent:
        """
        Validate and parse a webhook payload.

        Returns a WebhookEvent.

        Raises:
            InvalidWebhookSignatureError: When the webhook signature cannot be validated.
        """
        self.verify_signature(headers, auth=auth)
        body = payload.decode("utf-8") if isinstance(payload, bytes | bytearray) else payload
        return WebhookEvent.model_validate(json.loads(body))

    def webhook_payload(
        self,
        webhook_url: str,
        *,
        auth: WebhookAuthConfig | None = None,
    ) -> dict[str, str]:
        """
        Return fields for webhook configuration when creating a transcription.
        """
        payload = {"webhook_url": webhook_url}
        auth_config = auth or _resolve_webhook_auth(
            self._webhook_header,
            self._webhook_secret,
        )
        if auth_config is not None:
            payload["webhook_auth_header_name"] = auth_config.name
            payload["webhook_auth_header_value"] = auth_config.value
        return payload
