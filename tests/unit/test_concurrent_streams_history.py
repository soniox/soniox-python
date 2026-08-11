"""
Tests for ``client.concurrency_limits.history`` - per-period concurrent
stream aggregates. Pins the wire contract (URL, query params) and parsing.
"""

from __future__ import annotations

import pytest
import respx
from httpx import Response

from soniox.client import AsyncSonioxClient, SonioxClient
from tests.helpers import BASE_URL

HISTORY_URL = f"{BASE_URL}/concurrent-streams-history"

START_TIME = "2026-04-28T09:00:00Z"
END_TIME = "2026-04-28T10:00:00Z"


def _response() -> dict:
    return {
        "kind": "tts",
        "entries": [
            {
                "period_start": "2026-04-28T09:00:00Z",
                "period_sec": 60,
                "sample_min": 0,
                "sample_max": 4,
                "sample_sum": 21,
                "sample_count": 9,
                "total_count": 1,
            },
            {
                "period_start": "2026-04-28T09:01:00Z",
                "period_sec": 60,
                "sample_min": 0,
                "sample_max": 0,
                "sample_sum": 0,
                "sample_count": 0,
                "total_count": 0,
            },
        ],
    }


@respx.mock
def test_history_sends_all_query_params(client: SonioxClient) -> None:
    route = respx.get(HISTORY_URL).mock(return_value=Response(200, json=_response()))

    client.concurrency_limits.history(START_TIME, END_TIME, period_sec=60, kind="tts")

    assert dict(route.calls.last.request.url.params) == {
        "start_time": START_TIME,
        "end_time": END_TIME,
        "period_sec": "60",
        "kind": "tts",
    }


@respx.mock
def test_history_parses_entries(client: SonioxClient) -> None:
    respx.get(HISTORY_URL).mock(return_value=Response(200, json=_response()))

    result = client.concurrency_limits.history(START_TIME, END_TIME, period_sec=60, kind="tts")

    assert result.kind == "tts"
    assert result.entries[0].sample_max == 4
    assert result.entries[0].period_start.isoformat() == "2026-04-28T09:00:00+00:00"
    # Idle periods are returned as zeros rather than omitted.
    assert result.entries[1].sample_count == 0


@pytest.mark.asyncio
@respx.mock
async def test_async_history_matches_sync(async_client: AsyncSonioxClient) -> None:
    route = respx.get(HISTORY_URL).mock(return_value=Response(200, json=_response()))

    result = await async_client.concurrency_limits.history(
        START_TIME, END_TIME, period_sec=3600, kind="stt"
    )

    assert dict(route.calls.last.request.url.params)["period_sec"] == "3600"
    assert result.entries[0].period_sec == 60
