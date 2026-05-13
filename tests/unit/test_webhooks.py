"""
Tests for webhook signature verification, event parsing, and payload helpers.

Covers both the sync and async webhook clients (they share implementation,
but we exercise both so that future divergence is caught).
"""

from __future__ import annotations

import json

import pytest

from soniox.client import AsyncSonioxClient, SonioxClient
from soniox.errors import InvalidWebhookSignatureError
from soniox.types import WebhookAuthConfig

SECRET = "secret123"


@pytest.fixture(params=["sync", "async"])
def webhooks(request: pytest.FixtureRequest) -> object:
    """Parametrized fixture yielding the `webhooks` namespace from each client.

    Both clients share the same webhook implementation; this ensures neither
    side silently drops the behavior.
    """
    if request.param == "sync":
        return SonioxClient(api_key="test", webhook_secret=SECRET).webhooks
    return AsyncSonioxClient(api_key="test", webhook_secret=SECRET).webhooks


# ---------------------------------------------------------------------------
# verify_signature
# ---------------------------------------------------------------------------


def test_verify_signature_ok(webhooks) -> None:
    webhooks.verify_signature({"X-Soniox-Webhook-Secret": SECRET})


def test_verify_signature_case_insensitive_header(webhooks) -> None:
    # Real HTTP frameworks may lowercase headers. The SDK must match regardless.
    webhooks.verify_signature({"x-soniox-webhook-secret": SECRET})


def test_verify_signature_rejects_wrong_value(webhooks) -> None:
    with pytest.raises(InvalidWebhookSignatureError):
        webhooks.verify_signature({"X-Soniox-Webhook-Secret": "nope"})


def test_verify_signature_rejects_missing_header(webhooks) -> None:
    with pytest.raises(InvalidWebhookSignatureError):
        webhooks.verify_signature({})


def test_verify_signature_custom_auth_overrides_client_default(webhooks) -> None:
    # Explicit auth config takes precedence over whatever the client was built with.
    auth = WebhookAuthConfig(name="X-Custom", value="custom")
    webhooks.verify_signature({"X-Custom": "custom"}, auth=auth)
    with pytest.raises(InvalidWebhookSignatureError):
        webhooks.verify_signature({"X-Custom": "wrong"}, auth=auth)


def test_verify_signature_noop_without_secret() -> None:
    """Client built without a secret skips verification. Matches documented behavior."""
    api = SonioxClient(api_key="test").webhooks
    api.verify_signature({})  # must not raise


# ---------------------------------------------------------------------------
# unwrap
# ---------------------------------------------------------------------------


def test_unwrap_parses_event(webhooks) -> None:
    payload = json.dumps({"id": "t1", "status": "completed"})
    event = webhooks.unwrap(payload, {"X-Soniox-Webhook-Secret": SECRET})
    assert event.id == "t1"
    assert event.status == "completed"


def test_unwrap_accepts_bytes(webhooks) -> None:
    payload = json.dumps({"id": "t1", "status": "completed"}).encode()
    event = webhooks.unwrap(payload, {"X-Soniox-Webhook-Secret": SECRET})
    assert event.id == "t1"


def test_unwrap_rejects_bad_signature(webhooks) -> None:
    payload = json.dumps({"id": "t1", "status": "completed"})
    with pytest.raises(InvalidWebhookSignatureError):
        webhooks.unwrap(payload, {"X-Soniox-Webhook-Secret": "wrong"})


def test_unwrap_rejects_malformed_json(webhooks) -> None:
    with pytest.raises(json.JSONDecodeError):
        webhooks.unwrap("not-json", {"X-Soniox-Webhook-Secret": SECRET})


def test_unwrap_rejects_invalid_event_schema(webhooks) -> None:
    from pydantic import ValidationError

    payload = json.dumps({"id": "", "status": "unknown-status"})
    with pytest.raises(ValidationError):
        webhooks.unwrap(payload, {"X-Soniox-Webhook-Secret": SECRET})


# ---------------------------------------------------------------------------
# webhook_payload
# ---------------------------------------------------------------------------


def test_webhook_payload_includes_default_header(webhooks) -> None:
    payload = webhooks.webhook_payload("https://me.com/hook")
    assert payload == {
        "webhook_url": "https://me.com/hook",
        "webhook_auth_header_name": "X-Soniox-Webhook-Secret",
        "webhook_auth_header_value": SECRET,
    }


def test_webhook_payload_uses_custom_auth(webhooks) -> None:
    auth = WebhookAuthConfig(name="X-Custom", value="custom")
    payload = webhooks.webhook_payload("https://me.com/hook", auth=auth)
    assert payload["webhook_auth_header_name"] == "X-Custom"
    assert payload["webhook_auth_header_value"] == "custom"


def test_webhook_payload_omits_auth_when_no_secret() -> None:
    api = SonioxClient(api_key="test").webhooks
    payload = api.webhook_payload("https://me.com/hook")
    assert payload == {"webhook_url": "https://me.com/hook"}


def test_webhook_secret_resolves_from_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SONIOX_API_WEBHOOK_SECRET", "env_secret")
    api = SonioxClient(api_key="test").webhooks
    payload = api.webhook_payload("https://me.com/hook")
    assert payload["webhook_auth_header_value"] == "env_secret"
