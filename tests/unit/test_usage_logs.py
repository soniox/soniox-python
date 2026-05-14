"""
Tests for ``client.usage_logs`` - listing usage-log entries by time window
with pagination, sort order, and the ``list_all`` iterator.

These tests pin the wire contract (URL, query params) and the SDK's
pagination loop. Polyfactory builds entries so the test doesn't break
when new fields land on ``UsageLogEntry``.
"""

from __future__ import annotations

import respx
from httpx import Response

from soniox.client import AsyncSonioxClient, SonioxClient
from soniox.types import GetUsageLogsResponse, UsageLogEntry
from tests.helpers import BASE_URL, build

USAGE_LOGS_URL = f"{BASE_URL}/usage-logs"

START_TIME = "2026-01-01T00:00:00Z"
END_TIME = "2026-02-01T00:00:00Z"


def _response(*, entries: int = 2, next_cursor: str | None = None) -> dict:
    """Build a realistic ``GetUsageLogsResponse`` JSON payload."""
    payload = build(GetUsageLogsResponse)
    payload.usage_logs = [build(UsageLogEntry) for _ in range(entries)]
    payload.next_page_cursor = next_cursor
    return payload.model_dump(mode="json")


# ---------------------------------------------------------------------------
# Wire contract: URL + query params
# ---------------------------------------------------------------------------


@respx.mock
def test_list_sends_required_query_params(client: SonioxClient) -> None:
    route = respx.get(USAGE_LOGS_URL).mock(return_value=Response(200, json=_response()))

    client.usage_logs.list(start_time=START_TIME, end_time=END_TIME)

    params = dict(route.calls.last.request.url.params)
    assert params["start_time"] == START_TIME
    assert params["end_time"] == END_TIME
    # Defaults propagate so the server sees the explicit value the SDK chose.
    assert params["limit"] == "1000"
    assert params["sort"] == "end_time_asc"


@respx.mock
def test_list_omits_cursor_when_none(client: SonioxClient) -> None:
    """``exclude_none=True`` should drop the cursor on the first page."""
    route = respx.get(USAGE_LOGS_URL).mock(return_value=Response(200, json=_response()))

    client.usage_logs.list(start_time=START_TIME, end_time=END_TIME)

    assert "cursor" not in dict(route.calls.last.request.url.params)


@respx.mock
def test_list_forwards_cursor_and_sort(client: SonioxClient) -> None:
    route = respx.get(USAGE_LOGS_URL).mock(return_value=Response(200, json=_response()))

    client.usage_logs.list(
        start_time=START_TIME,
        end_time=END_TIME,
        sort="end_time_desc",
        cursor="page_2",
    )

    params = dict(route.calls.last.request.url.params)
    assert params["sort"] == "end_time_desc"
    assert params["cursor"] == "page_2"


# ---------------------------------------------------------------------------
# Response parsing
# ---------------------------------------------------------------------------


@respx.mock
def test_list_parses_response_into_typed_model(client: SonioxClient) -> None:
    body = _response(entries=3, next_cursor="next_page")
    respx.get(USAGE_LOGS_URL).mock(return_value=Response(200, json=body))

    result = client.usage_logs.list(start_time=START_TIME, end_time=END_TIME)

    assert len(result.usage_logs) == 3
    assert all(isinstance(e, UsageLogEntry) for e in result.usage_logs)
    assert result.next_page_cursor == "next_page"


# ---------------------------------------------------------------------------
# list_all pagination
# ---------------------------------------------------------------------------


@respx.mock
def test_list_all_follows_cursors_until_exhausted(client: SonioxClient) -> None:
    """``list_all`` must walk every page and stop when the cursor is None."""
    pages = iter(
        [
            Response(200, json=_response(entries=2, next_cursor="p2")),
            Response(200, json=_response(entries=2, next_cursor="p3")),
            Response(200, json=_response(entries=1, next_cursor=None)),
        ]
    )
    route = respx.get(USAGE_LOGS_URL).mock(side_effect=lambda req: next(pages))

    entries = list(client.usage_logs.list_all(start_time=START_TIME, end_time=END_TIME))

    assert route.call_count == 3
    assert len(entries) == 5
    # Cursor of the 2nd and 3rd request must echo the previous page's cursor.
    assert dict(route.calls[1].request.url.params)["cursor"] == "p2"
    assert dict(route.calls[2].request.url.params)["cursor"] == "p3"


@respx.mock
def test_list_all_stops_on_first_page_when_no_cursor(client: SonioxClient) -> None:
    route = respx.get(USAGE_LOGS_URL).mock(
        return_value=Response(200, json=_response(entries=2, next_cursor=None))
    )

    entries = list(client.usage_logs.list_all(start_time=START_TIME, end_time=END_TIME))

    assert route.call_count == 1
    assert len(entries) == 2


# ---------------------------------------------------------------------------
# Async parity
# ---------------------------------------------------------------------------


@respx.mock
async def test_async_list_sends_required_params(async_client: AsyncSonioxClient) -> None:
    route = respx.get(USAGE_LOGS_URL).mock(return_value=Response(200, json=_response()))

    await async_client.usage_logs.list(start_time=START_TIME, end_time=END_TIME)

    params = dict(route.calls.last.request.url.params)
    assert params["start_time"] == START_TIME
    assert params["end_time"] == END_TIME


@respx.mock
async def test_async_list_all_follows_cursors(async_client: AsyncSonioxClient) -> None:
    pages = iter(
        [
            Response(200, json=_response(entries=2, next_cursor="p2")),
            Response(200, json=_response(entries=1, next_cursor=None)),
        ]
    )
    respx.get(USAGE_LOGS_URL).mock(side_effect=lambda req: next(pages))

    entries = [
        e
        async for e in async_client.usage_logs.list_all(
            start_time=START_TIME, end_time=END_TIME
        )
    ]

    assert len(entries) == 3
