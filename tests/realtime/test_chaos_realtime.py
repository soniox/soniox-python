"""
Deterministic failure-injection tests for the realtime SDK.

Instead of randomized chaos, we push specific failures through the mock
WebSocket and verify that the SDK translates them into the documented
exception shape:

- Connection dropped during recv → ``receive_events()`` stops cleanly (empty
  recv is treated as EOF by the session).
- Connection dropped during send → ``send_byte_chunk`` raises
  ``SonioxRealtimeError``.
- Initial handshake failure → ``__enter__`` raises ``SonioxRealtimeError``.
- Unexpected server exception (non-ConnectionClosed) during recv → propagates.
- Timeline-scheduled errors via ``RealtimeTester`` reach the consumer as
  ``event.error_code``-bearing events.
"""

from __future__ import annotations

from unittest.mock import patch

import pytest
from websockets.exceptions import ConnectionClosed

from soniox.client import AsyncSonioxClient, SonioxClient
from soniox.errors import SonioxRealtimeError
from soniox.types.realtime import RealtimeSTTConfig

from .mock_ws import AsyncMockWebSocket, MockWebSocket

CONFIG = RealtimeSTTConfig(model="v1")


# ---------------------------------------------------------------------------
# Connection closed mid-stream (recv side)
# ---------------------------------------------------------------------------


def test_connection_closed_during_recv_stops_iteration(client: SonioxClient) -> None:
    """The SDK maps a mid-stream ConnectionClosed to graceful end-of-stream."""
    ws = MockWebSocket()
    ws.push_recv({"tokens": [{"text": "partial", "is_final": False}]})
    ws.push_recv({"tokens": [{"text": "final", "is_final": True}]})
    ws.push_recv_error(ConnectionClosed(None, None))

    with patch("soniox.realtime.stt.sync_ws_connect", return_value=ws):
        with client.realtime.stt.connect(config=CONFIG) as session:
            events = list(session.receive_events())

    # Events delivered before the drop are still surfaced.
    assert len(events) == 2
    assert events[1].tokens[0].text == "final"


async def test_connection_closed_during_recv_stops_iteration_async(
    async_client: AsyncSonioxClient,
) -> None:
    ws = AsyncMockWebSocket()
    ws.push_recv({"tokens": [{"text": "partial", "is_final": False}]})
    ws.push_recv_error(ConnectionClosed(None, None))

    with patch("soniox.realtime.async_stt.async_ws_connect", return_value=ws):
        async with async_client.realtime.stt.connect(config=CONFIG) as session:
            events = [event async for event in session.receive_events()]

    assert len(events) == 1


# ---------------------------------------------------------------------------
# Failure on send
# ---------------------------------------------------------------------------


def test_send_on_closed_connection_raises(client: SonioxClient) -> None:
    ws = MockWebSocket()
    ws.close_after_recv()

    with patch("soniox.realtime.stt.sync_ws_connect", return_value=ws):
        with client.realtime.stt.connect(config=CONFIG) as session:
            ws.closed = True  # simulate the peer going away
            with pytest.raises(SonioxRealtimeError):
                session.send_byte_chunk(b"audio")


async def test_send_on_closed_connection_raises_async(
    async_client: AsyncSonioxClient,
) -> None:
    ws = AsyncMockWebSocket()
    ws.close_after_recv()

    with patch("soniox.realtime.async_stt.async_ws_connect", return_value=ws):
        async with async_client.realtime.stt.connect(config=CONFIG) as session:
            ws.closed = True
            with pytest.raises(SonioxRealtimeError):
                await session.send_byte_chunk(b"audio")


# ---------------------------------------------------------------------------
# Handshake failure
# ---------------------------------------------------------------------------


def test_handshake_failure_wraps_as_realtime_error(client: SonioxClient) -> None:
    def _raise(*_args: object) -> None:
        raise ConnectionClosed(None, None)

    with patch("soniox.realtime.stt.sync_ws_connect", side_effect=_raise):
        with pytest.raises(SonioxRealtimeError):
            with client.realtime.stt.connect(config=CONFIG):
                pass


# ---------------------------------------------------------------------------
# Non-ConnectionClosed recv error is not swallowed
# ---------------------------------------------------------------------------


def test_unexpected_recv_error_propagates(client: SonioxClient) -> None:
    ws = MockWebSocket()
    ws.push_recv_error(RuntimeError("kaboom"))

    with patch("soniox.realtime.stt.sync_ws_connect", return_value=ws):
        with client.realtime.stt.connect(config=CONFIG) as session:
            with pytest.raises(RuntimeError, match="kaboom"):
                list(session.receive_events())


# ---------------------------------------------------------------------------
# Server-side error events surface to the consumer
# ---------------------------------------------------------------------------


def test_server_error_event_surfaces_to_consumer(client: SonioxClient) -> None:
    """STT realtime treats error events as data, not exceptions - the SDK
    must forward an ``error_code``-bearing event to the consumer instead of
    raising."""
    ws = MockWebSocket()
    ws.push_recv({"error_code": 429, "error_message": "rate limited"})

    with patch("soniox.realtime.stt.sync_ws_connect", return_value=ws):
        with client.realtime.stt.connect(config=CONFIG) as session:
            events = list(session.receive_events())

    assert any(e.error_code == 429 for e in events), events


async def test_server_error_event_surfaces_to_consumer_async(
    async_client: AsyncSonioxClient,
) -> None:
    ws = AsyncMockWebSocket()
    ws.push_recv({"error_code": 429, "error_message": "rate limited"})

    with patch("soniox.realtime.async_stt.async_ws_connect", return_value=ws):
        async with async_client.realtime.stt.connect(config=CONFIG) as session:
            events = [event async for event in session.receive_events()]

    assert any(e.error_code == 429 for e in events), events
