"""Tests for `client.organization` - sync + async organization administration."""

from __future__ import annotations

import json

import pytest
import respx
from httpx import Response

from soniox.client import AsyncSonioxClient, SonioxClient
from soniox.errors import SonioxNotFoundError
from soniox.types import (
    CreateProjectApiKeyResponse,
    GetOrganizationBalanceResponse,
    GetOrganizationLimitsResponse,
    GetOrganizationMonthlyUsageResponse,
    GetOrganizationProjectsResponse,
    GetOrganizationResponse,
    GetOrganizationUsageSummaryResponse,
    GetProjectApiKeysResponse,
)
from tests.helpers import BASE_URL, api_error_body, build

ORGANIZATION_URL = f"{BASE_URL}/organization"
PROJECT_ID = "11111111-1111-1111-1111-111111111111"
KEY_ID = "22222222-2222-2222-2222-222222222222"
API_KEYS_URL = f"{ORGANIZATION_URL}/projects/{PROJECT_ID}/api-keys"

START_TIME = "2026-04-01T00:00:00Z"
END_TIME = "2026-04-03T00:00:00Z"


@respx.mock
def test_get_returns_typed_response(client: SonioxClient) -> None:
    body = build(GetOrganizationResponse).model_dump(mode="json")
    respx.get(ORGANIZATION_URL).mock(return_value=Response(200, json=body))

    result = client.organization.get()

    assert isinstance(result, GetOrganizationResponse)
    assert result.id == body["id"]


@respx.mock
def test_balance_keeps_money_as_strings(client: SonioxClient) -> None:
    """Amounts stay decimal strings - no float rounding on the way through."""
    body = build(GetOrganizationBalanceResponse).model_dump(mode="json")
    body["available_balance_usd"] = "12.3400000000"
    respx.get(f"{ORGANIZATION_URL}/balance").mock(return_value=Response(200, json=body))

    result = client.organization.balance()

    assert result.available_balance_usd == "12.3400000000"


@respx.mock
def test_balance_autopay_off_parses_as_none(client: SonioxClient) -> None:
    body = build(GetOrganizationBalanceResponse).model_dump(mode="json")
    body["autopay_enabled"] = False
    body["autopay_threshold_usd"] = None
    body["autopay_amount_usd"] = None
    respx.get(f"{ORGANIZATION_URL}/balance").mock(return_value=Response(200, json=body))

    result = client.organization.balance()

    assert result.autopay_threshold_usd is None
    assert result.autopay_amount_usd is None


@respx.mock
def test_limits_returns_a_region_entry(client: SonioxClient) -> None:
    body = build(GetOrganizationLimitsResponse).model_dump(mode="json")
    respx.get(f"{ORGANIZATION_URL}/limits").mock(return_value=Response(200, json=body))

    result = client.organization.limits()

    assert isinstance(result, GetOrganizationLimitsResponse)
    assert result.regions[0].region == body["regions"][0]["region"]


@respx.mock
def test_monthly_usage_omits_month_by_default(client: SonioxClient) -> None:
    body = build(GetOrganizationMonthlyUsageResponse).model_dump(mode="json")
    route = respx.get(f"{ORGANIZATION_URL}/usage/monthly").mock(
        return_value=Response(200, json=body)
    )

    client.organization.monthly_usage()

    assert dict(route.calls.last.request.url.params) == {}


@respx.mock
def test_monthly_usage_sends_the_month(client: SonioxClient) -> None:
    body = build(GetOrganizationMonthlyUsageResponse).model_dump(mode="json")
    route = respx.get(f"{ORGANIZATION_URL}/usage/monthly").mock(
        return_value=Response(200, json=body)
    )

    client.organization.monthly_usage("2026-04")

    assert dict(route.calls.last.request.url.params) == {"month": "2026-04"}


@respx.mock
def test_monthly_usage_without_a_budget_parses_as_none(client: SonioxClient) -> None:
    body = build(GetOrganizationMonthlyUsageResponse).model_dump(mode="json")
    body["monthly_budget_usd"] = None
    body["remaining_budget_usd"] = None
    body["budget_exhausted"] = None
    respx.get(f"{ORGANIZATION_URL}/usage/monthly").mock(return_value=Response(200, json=body))

    result = client.organization.monthly_usage()

    assert result.monthly_budget_usd is None
    assert result.budget_exhausted is None


@respx.mock
def test_usage_summary_sends_window_as_query_params(client: SonioxClient) -> None:
    body = build(GetOrganizationUsageSummaryResponse).model_dump(mode="json")
    route = respx.get(f"{ORGANIZATION_URL}/usage/summary").mock(
        return_value=Response(200, json=body)
    )

    result = client.organization.usage_summary(START_TIME, END_TIME)

    assert dict(route.calls.last.request.url.params) == {
        "start_time": START_TIME,
        "end_time": END_TIME,
    }
    assert isinstance(result, GetOrganizationUsageSummaryResponse)


@respx.mock
def test_projects_returns_every_project(client: SonioxClient) -> None:
    body = build(GetOrganizationProjectsResponse).model_dump(mode="json")
    respx.get(f"{ORGANIZATION_URL}/projects").mock(return_value=Response(200, json=body))

    result = client.organization.projects()

    assert len(result.projects) == len(body["projects"])


@respx.mock
def test_list_project_api_keys_hits_the_project_path(client: SonioxClient) -> None:
    body = build(GetProjectApiKeysResponse).model_dump(mode="json")
    route = respx.get(API_KEYS_URL).mock(return_value=Response(200, json=body))

    result = client.organization.list_project_api_keys(PROJECT_ID)

    assert PROJECT_ID in str(route.calls.last.request.url)
    assert isinstance(result, GetProjectApiKeysResponse)


@respx.mock
def test_create_project_api_key_sends_name_and_permissions(client: SonioxClient) -> None:
    body = build(CreateProjectApiKeyResponse).model_dump(mode="json")
    route = respx.post(API_KEYS_URL).mock(return_value=Response(201, json=body))

    result = client.organization.create_project_api_key(
        PROJECT_ID, name="ci", permissions=["models:read", "usage:read"]
    )

    assert json.loads(route.calls.last.request.content) == {
        "name": "ci",
        "permissions": ["models:read", "usage:read"],
    }
    assert result.key == body["key"]


@respx.mock
def test_delete_project_api_key_accepts_204(client: SonioxClient) -> None:
    route = respx.delete(f"{API_KEYS_URL}/{KEY_ID}").mock(return_value=Response(204))

    assert client.organization.delete_project_api_key(PROJECT_ID, KEY_ID) is None
    assert KEY_ID in str(route.calls.last.request.url)


@respx.mock
def test_delete_project_api_key_raises_on_missing_key(client: SonioxClient) -> None:
    respx.delete(f"{API_KEYS_URL}/{KEY_ID}").mock(
        return_value=Response(404, json=api_error_body(404))
    )

    with pytest.raises(SonioxNotFoundError):
        client.organization.delete_project_api_key(PROJECT_ID, KEY_ID)


@respx.mock
async def test_async_get(async_client: AsyncSonioxClient) -> None:
    body = build(GetOrganizationResponse).model_dump(mode="json")
    respx.get(ORGANIZATION_URL).mock(return_value=Response(200, json=body))

    result = await async_client.organization.get()

    assert result.id == body["id"]


@respx.mock
async def test_async_create_project_api_key(async_client: AsyncSonioxClient) -> None:
    body = build(CreateProjectApiKeyResponse).model_dump(mode="json")
    respx.post(API_KEYS_URL).mock(return_value=Response(201, json=body))

    result = await async_client.organization.create_project_api_key(
        PROJECT_ID, name="ci", permissions=["models:read"]
    )

    assert result.key == body["key"]


@respx.mock
async def test_async_delete_project_api_key(async_client: AsyncSonioxClient) -> None:
    respx.delete(f"{API_KEYS_URL}/{KEY_ID}").mock(return_value=Response(204))

    assert await async_client.organization.delete_project_api_key(PROJECT_ID, KEY_ID) is None
