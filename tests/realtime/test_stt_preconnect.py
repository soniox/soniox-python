"""Tests for STT pre-connect (idle WebSocket + deferred config)."""

from __future__ import annotations

import asyncio
from unittest.mock import patch

import pytest

from soniox.client import AsyncSonioxClient, SonioxClient
from soniox.errors import SonioxRealtimeError
from soniox.types.realtime import RealtimeSTTConfig

from .mock_ws import AsyncMockWebSocket, MockWebSocket

CONFIG = RealtimeSTTConfig(model="v1", audio_format="ogg")


def _patch_sync_ws(ws: MockWebSocket):
    return patch("soniox.realtime._transport.sync_ws_connect", return_value=ws)


def _patch_async_ws(ws: AsyncMockWebSocket):
    return patch("soniox.realtime._transport.async_ws_connect", return_value=ws)


def test_connect_idle_defers_config(client: SonioxClient) -> None:
    ws = MockWebSocket()
    ws.close_after_recv()

    with _patch_sync_ws(ws):
        with client.realtime.stt.connect_idle() as conn:
            assert conn.connected
            assert ws.sent_messages == []
            conn.start_idle_keepalive(interval_sec=0.01)
            conn.stop_idle_keepalive()
            stream = conn.start_session(config=CONFIG)
            stream.send_byte_chunk(b"page1")
            stream.finish()

    assert ws.sent_messages[0]["model"] == "v1"
    assert ws.sent_messages[0]["audio_format"] == "ogg"
    assert ws.sent_messages[1] == b"page1"
    assert ws.sent_messages[2] == ""


def test_idle_keepalive_before_session(client: SonioxClient) -> None:
    ws = MockWebSocket()
    ws.close_after_recv()

    with _patch_sync_ws(ws):
        with client.realtime.stt.connect_idle() as conn:
            conn.keep_alive()
            stream = conn.start_session(config=CONFIG)
            stream.finish()

    assert ws.sent_messages[0] == {"type": "keepalive"}
    assert ws.sent_messages[1]["model"] == "v1"


def test_connection_pool_warmup_sends_no_config(client: SonioxClient) -> None:
    ws = MockWebSocket()
    ws.close_after_recv()

    with _patch_sync_ws(ws):
        with client.realtime.stt.create_connection_pool(
            pool_size=2,
            idle_keepalive=False,
        ) as pool:
            assert pool.idle_count == 2
            assert ws.sent_messages == []


def test_connection_pool_sends_keepalive_by_default(client: SonioxClient) -> None:
    ws = MockWebSocket()
    ws.close_after_recv()

    with _patch_sync_ws(ws):
        with client.realtime.stt.create_connection_pool(
            pool_size=1,
            keepalive_interval_sec=0.01,
        ) as pool:
            import time

            time.sleep(0.03)
            assert {"type": "keepalive"} in ws.sent_messages
            assert all(
                msg == {"type": "keepalive"} or not isinstance(msg, dict) or "model" not in msg
                for msg in ws.sent_messages
            )


def test_pool_refreshes_link_near_max_lifetime(client: SonioxClient) -> None:
    ws1 = MockWebSocket()
    ws1.close_after_recv()
    ws2 = MockWebSocket()
    ws2.close_after_recv()
    sockets = iter([ws1, ws2])

    import time

    with patch("soniox.realtime._transport.sync_ws_connect", side_effect=lambda *a, **k: next(sockets)):
        with client.realtime.stt.create_connection_pool(
            pool_size=1,
            idle_keepalive=False,
            idle_max_lifetime_sec=0.05,
            idle_refresh_before_sec=0.03,
        ) as pool:
            time.sleep(0.04)
            stream = pool.start_session(config=CONFIG)
            stream.finish()

    assert ws1.closed
    assert ws2.sent_messages[0]["model"] == "v1"


def test_borrow_removes_link_from_pool(client: SonioxClient) -> None:
    ws = MockWebSocket()
    ws.close_after_recv()

    with _patch_sync_ws(ws):
        with client.realtime.stt.create_connection_pool(
            pool_size=2,
            idle_keepalive=False,
        ) as pool:
            assert pool.idle_count == 2
            with patch.object(pool, "_replenish_one"):
                conn = pool.borrow_connection()
            assert pool.idle_count == 1
            conn.discard()


def test_borrow_creates_immediately_when_pool_empty(client: SonioxClient) -> None:
    ws = MockWebSocket()
    ws.close_after_recv()

    with _patch_sync_ws(ws):
        pool = client.realtime.stt.create_connection_pool(
            pool_size=1,
            idle_keepalive=False,
        )
        try:
            assert pool.idle_count == 0
            with patch.object(pool, "_replenish_one"):
                conn = pool.borrow_connection()
            assert conn.connected
            assert pool.idle_count == 0
            conn.discard()
        finally:
            pool.close()


def test_preconnect_pool_start_session(client: SonioxClient) -> None:
    ws1 = MockWebSocket()
    ws1.close_after_recv()
    ws2 = MockWebSocket()
    ws2.close_after_recv()
    sockets = iter([ws1, ws2])

    with patch("soniox.realtime._transport.sync_ws_connect", side_effect=lambda *a, **k: next(sockets)):
        with client.realtime.stt.create_connection_pool(
            pool_size=1,
            idle_keepalive=False,
        ) as pool:
            assert pool.idle_count == 1
            stream = pool.start_session(config=CONFIG)
            stream.send_byte_chunk(b"audio")
            stream.finish()

    assert ws1.sent_messages[0]["model"] == "v1"
    assert ws1.sent_messages[1] == b"audio"


async def test_async_connect_idle_defers_config(async_client: AsyncSonioxClient) -> None:
    ws = AsyncMockWebSocket()
    ws.close_after_recv()

    with _patch_async_ws(ws):
        async with async_client.realtime.stt.connect_idle() as conn:
            assert conn.connected
            assert ws.sent_messages == []
            stream = await conn.start_session(config=CONFIG)
            await stream.send_byte_chunk(b"page1")
            await stream.finish()

    assert ws.sent_messages[0]["model"] == "v1"
    assert ws.sent_messages[1] == b"page1"
    assert ws.sent_messages[2] == ""


async def test_async_preconnect_pool_replenishes(async_client: AsyncSonioxClient) -> None:
    ws1 = AsyncMockWebSocket()
    ws1.close_after_recv()
    ws2 = AsyncMockWebSocket()
    ws2.close_after_recv()
    sockets = iter([ws1, ws2])

    with patch(
        "soniox.realtime._transport.async_ws_connect",
        side_effect=lambda *a, **k: next(sockets),
    ):
        async with async_client.realtime.stt.create_connection_pool(
            pool_size=1,
            idle_keepalive=False,
        ) as pool:
            stream = await pool.start_session(config=CONFIG)
            await stream.finish()
            await asyncio.sleep(0.05)
            assert pool.idle_count == 1


def test_connect_uses_internal_connection_pool(client: SonioxClient) -> None:
    """Default connect() claims a pre-connected link from the internal pool."""
    ws = MockWebSocket()
    ws.close_after_recv()
    config = RealtimeSTTConfig(model="v1", audio_format="ogg")

    pooled_client = SonioxClient(api_key="test_key", stt_connection_pool_size=1)
    try:
        with patch("soniox.realtime._transport.sync_ws_connect", return_value=ws):
            pooled_client.realtime.stt.warmup_connection_pool()
            assert all(
                not (isinstance(message, dict) and "model" in message)
                for message in ws.sent_messages
            )

            with pooled_client.realtime.stt.connect(
                config=config,
                use_connection_pool=True,
            ) as session:
                session.send_byte_chunk(b"audio")
                session.finish()

        assert ws.sent_messages[0]["model"] == "v1"
        assert ws.sent_messages[1] == b"audio"
    finally:
        pooled_client.close()


def test_session_connection_discarded_not_returned_to_pool(client: SonioxClient) -> None:
    ws1 = MockWebSocket()
    ws1.close_after_recv()
    ws2 = MockWebSocket()
    ws2.close_after_recv()
    ws3 = MockWebSocket()
    ws3.close_after_recv()
    sockets = iter([ws1, ws2, ws3])

    with patch("soniox.realtime._transport.sync_ws_connect", side_effect=lambda *a, **k: next(sockets)):
        with client.realtime.stt.create_connection_pool(
            pool_size=1,
            idle_keepalive=False,
        ) as pool:
            stream = pool.start_session(config=CONFIG)
            first_conn = stream._connection
            stream.finish()
            stream.close()
            assert ws1.closed
            assert not first_conn.connected

            with pytest.raises(SonioxRealtimeError, match="already been discarded"):
                first_conn.start_session(config=CONFIG)

            stream2 = pool.start_session(config=CONFIG)
            assert stream2._connection is not first_conn
            stream2.close()


def test_cannot_start_second_session_on_same_connection(client: SonioxClient) -> None:
    ws = MockWebSocket()
    ws.close_after_recv()

    with _patch_sync_ws(ws):
        with client.realtime.stt.connect_idle() as conn:
            conn.start_session(config=CONFIG)
            with pytest.raises(SonioxRealtimeError, match="already has an active session"):
                conn.start_session(config=CONFIG)
