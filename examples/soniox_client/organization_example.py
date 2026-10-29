import os

from soniox.client import SonioxClient
from soniox.errors import SonioxAPIError, SonioxPermissionDeniedError

# Every call below needs an organization API key, not a project key. It travels in the
# same Authorization header, so there is nothing to configure beyond the key itself.
ORGANIZATION_API_KEY = os.environ.get("SONIOX_ORGANIZATION_API_KEY", "")

MONTH = "2026-04"
START_TIME = "2026-04-01T00:00:00Z"
END_TIME = "2026-05-01T00:00:00Z"


def main() -> None:
    client = SonioxClient(api_key=ORGANIZATION_API_KEY)
    try:
        organization = client.organization.get()
        print(f"{organization.name} (id={organization.id})")

        balance = client.organization.balance()
        print(f"Available balance: ${balance.available_balance_usd}")
        if balance.balance_exhausted:
            print("  balance exhausted - requests are being refused")

        # Amounts are decimal strings throughout, never floats: pass them to Decimal
        # if you need arithmetic, so cents never round away.
        monthly = client.organization.monthly_usage(MONTH)
        print(f"{monthly.month}: ${monthly.usage_usd} used, ${monthly.api_usage_usd} via the API")
        for project in monthly.projects:
            print(f"  - {project.name}: ${project.usage_usd}")

        # The same per-day shape client.usage.summary() returns, split per project
        # instead of per model. Each entry's lists are aligned by index with `days`.
        summary = client.organization.usage_summary(START_TIME, END_TIME)
        print(f"Window total: ${summary.total.total_cost_usd}")

        limits = client.organization.limits()
        for region in limits.regions:
            print(f"  {region.region}: {region.transcribe_concurrent} concurrent STT sessions")

        for project in client.organization.projects().projects:
            keys = client.organization.list_project_api_keys(project.id)
            print(f"{project.name} ({project.region}): {len(keys.api_keys)} API keys")
            for key in keys.api_keys:
                print(f"  - {key.key_prefix}... {key.name} {key.permissions}")

        # Creating a key returns the secret once, in `key`, and never again - store it
        # before you drop the response:
        #
        #   created = client.organization.create_project_api_key(
        #       project.id, name="ci", permissions=["stt_async:write", "files:write"]
        #   )
        #   client.organization.delete_project_api_key(project.id, created.id)

    except SonioxPermissionDeniedError:
        print("That key is not an organization API key, or lacks the permission.")
    except SonioxAPIError as exc:
        print("Soniox API error:", exc)
        if exc.request_id:
            print("  request_id:", exc.request_id)
    finally:
        client.close()


if __name__ == "__main__":
    main()
