"""
Tests for ``client.usage.summary`` - daily cost and activity aggregates.

Pins the wire contract (URL, query params) and that the index-aligned
per-day lists survive the round trip.
"""

from __future__ import annotations

import pytest
import respx
from httpx import Response

from soniox.client import AsyncSonioxClient, SonioxClient
from soniox.types import GetUsageSummaryResponse
from tests.helpers import BASE_URL

SUMMARY_URL = f"{BASE_URL}/usage/summary"

START_TIME = "2026-04-01T00:00:00Z"
END_TIME = "2026-04-03T00:00:00Z"


def _entry(model: str | None) -> dict:
    return {
        "model": model,
        "days": ["2026-04-01", "2026-04-02"],
        "total_cost_usd": "0.2567250000",
        "total_input_cost_usd": "0.0415500000",
        "total_output_cost_usd": "0.2151750000",
        "total_duration_cost_usd": "0.0000000000",
        "cost_usd": ["0.1711500000", "0.0855750000"],
        "input_cost_usd": ["0.0277000000", "0.0138500000"],
        "output_cost_usd": ["0.1434500000", "0.0717250000"],
        "duration_cost_usd": ["0.0000000000", "0.0000000000"],
        "total_num_requests": 285,
        "total_input_text_tokens": 4800,
        "total_input_audio_tokens": 15000,
        "total_input_audio_duration_ms": 1800000,
        "total_output_text_tokens": 10800,
        "total_output_audio_tokens": 8250,
        "total_output_audio_duration_ms": 990000,
        "total_duration_ms": 0,
        "num_requests": [190, 95],
        "input_text_tokens": [3200, 1600],
        "input_audio_tokens": [10000, 5000],
        "input_audio_duration_ms": [1200000, 600000],
        "output_text_tokens": [7200, 3600],
        "output_audio_tokens": [5500, 2750],
        "output_audio_duration_ms": [660000, 330000],
        "duration_ms": [0, 0],
    }


def _response(*, models: list[str] | None = None) -> dict:
    return {
        "total": _entry(None),
        "models": [_entry(m) for m in (models if models is not None else ["stt-async-v5"])],
    }


@respx.mock
def test_summary_sends_window_as_query_params(client: SonioxClient) -> None:
    route = respx.get(SUMMARY_URL).mock(return_value=Response(200, json=_response()))

    client.usage.summary(start_time=START_TIME, end_time=END_TIME)

    params = dict(route.calls.last.request.url.params)
    assert params == {"start_time": START_TIME, "end_time": END_TIME}


@respx.mock
def test_summary_parses_entries(client: SonioxClient) -> None:
    respx.get(SUMMARY_URL).mock(return_value=Response(200, json=_response()))

    result = client.usage.summary(start_time=START_TIME, end_time=END_TIME)

    assert isinstance(result, GetUsageSummaryResponse)
    assert result.total.model is None
    assert result.total.total_cost_usd == "0.2567250000"
    assert [d.isoformat() for d in result.total.days] == ["2026-04-01", "2026-04-02"]
    # Per-day lists stay index-aligned with days.
    assert len(result.total.cost_usd) == len(result.total.days)
    assert result.models[0].model == "stt-async-v5"


@respx.mock
def test_summary_accepts_project_without_usage(client: SonioxClient) -> None:
    respx.get(SUMMARY_URL).mock(return_value=Response(200, json=_response(models=[])))

    result = client.usage.summary(start_time=START_TIME, end_time=END_TIME)

    assert result.models == []


@pytest.mark.asyncio
@respx.mock
async def test_async_summary_matches_sync(async_client: AsyncSonioxClient) -> None:
    route = respx.get(SUMMARY_URL).mock(return_value=Response(200, json=_response()))

    result = await async_client.usage.summary(start_time=START_TIME, end_time=END_TIME)

    assert dict(route.calls.last.request.url.params) == {
        "start_time": START_TIME,
        "end_time": END_TIME,
    }
    assert result.total.model is None
