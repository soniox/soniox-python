from __future__ import annotations

import asyncio
import os

from soniox import AsyncSonioxClient
from soniox.types.webhooks import WebhookAuthConfig


async def main() -> None:
    api_key = os.environ.get("SONIOX_API_KEY")
    if not api_key:
        raise SystemExit("Please set SONIOX_API_KEY to run the async auth example.")

    async with AsyncSonioxClient(api_key=api_key) as client:
        temp_key = await client.auth.create_temporary_api_key(expires_in_seconds=1800)
        print("(async) Temporary API key:")
        print(f"  value: {temp_key.api_key}")
        print(f"  expires_at: {temp_key.expires_at}")

        webhook_payload = client.webhooks.webhook_payload(
            "https://example.com/soniox-webhook",
            auth=WebhookAuthConfig(name="Authorization", value="Bearer secret"),
        )
        print("\n(async) Webhook payload configured for transcription creation:")
        for key, value in webhook_payload.items():
            print(f"  {key}: {value}")


if __name__ == "__main__":
    asyncio.run(main())
