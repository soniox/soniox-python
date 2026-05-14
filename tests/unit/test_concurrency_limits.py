"""Tests for `client.concurrency_limits` - sync + async GET /concurrency-limits."""

from __future__ import annotations

import respx
from httpx import Response

from soniox.client import AsyncSonioxClient, SonioxClient
from soniox.types import GetConcurrencyLimitsResponse
from tests.helpers import BASE_URL, build

CONCURRENCY_URL = f"{BASE_URL}/concurrency-limits"


def _response() -> dict:
    return build(GetConcurrencyLimitsResponse).model_dump(mode="json")


@respx.mock
def test_get_returns_typed_response(client: SonioxClient) -> None:
    respx.get(CONCURRENCY_URL).mock(return_value=Response(200, json=_response()))

    result = client.concurrency_limits.get()

    assert isinstance(result, GetConcurrencyLimitsResponse)
    assert isinstance(result.project.current.transcribe_concurrent, int)
    assert isinstance(result.organization.limits.tts_concurrent, (int, type(None)))


@respx.mock
def test_get_sends_no_query_params(client: SonioxClient) -> None:
    route = respx.get(CONCURRENCY_URL).mock(return_value=Response(200, json=_response()))

    client.concurrency_limits.get()

    assert dict(route.calls.last.request.url.params) == {}


@respx.mock
async def test_get_async(async_client: AsyncSonioxClient) -> None:
    respx.get(CONCURRENCY_URL).mock(return_value=Response(200, json=_response()))

    result = await async_client.concurrency_limits.get()

    assert isinstance(result, GetConcurrencyLimitsResponse)


@respx.mock
def test_unlimited_returns_none(client: SonioxClient) -> None:
    """When a tier has no concurrency cap, limits.X should parse as None."""
    body = _response()
    body["project"]["limits"] = {"transcribe_concurrent": None, "tts_concurrent": None}
    respx.get(CONCURRENCY_URL).mock(return_value=Response(200, json=body))

    result = client.concurrency_limits.get()

    assert result.project.limits.transcribe_concurrent is None
    assert result.project.limits.tts_concurrent is None
