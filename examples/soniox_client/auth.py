from __future__ import annotations

import os

from soniox import SonioxClient
from soniox.types.webhooks import WebhookAuthConfig


def main() -> None:
    api_key = os.environ.get("SONIOX_API_KEY")
    if not api_key:
        raise SystemExit("Please set SONIOX_API_KEY to run the auth example.")

    with SonioxClient(api_key=api_key) as client:
        temp_key = client.auth.create_temporary_api_key(expires_in_seconds=1800)
        print("Temporary API key:")
        print(f"  value: {temp_key.api_key}")
        print(f"  expires_at: {temp_key.expires_at}")

        webhook_payload = client.webhooks.webhook_payload(
            "https://example.com/soniox-webhook",
            auth=WebhookAuthConfig(name="Authorization", value="Bearer secret"),
        )
        print("\nWebhook payload configured for transcription creation:")
        for key, value in webhook_payload.items():
            print(f"  {key}: {value}")


if __name__ == "__main__":
    main()
