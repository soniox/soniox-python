"""
Timing tests for the keepalive thread / task that runs while a realtime
session is paused.

Existing tests verify that ``session.pause()`` *triggers* the keepalive
machinery. These tests verify it actually *fires* at the configured interval
by monkeypatching ``KEEP_ALIVE_INTERVAL_SEC`` down to 10ms and observing
messages arriving on the mock socket.
"""

from __future__ import annotations

import asyncio
import time
from unittest.mock import patch

import pytest

from soniox.client import AsyncSonioxClient, SonioxClient
from soniox.types.realtime import RealtimeSTTConfig

from .mock_ws import AsyncMockWebSocket, MockWebSocket

CONFIG = RealtimeSTTConfig(model="v1")


def test_keepalive_thread_fires_while_paused(
    client: SonioxClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    ws = MockWebSocket()
    ws.close_after_recv()
    monkeypatch.setattr("soniox.realtime.stt.KEEP_ALIVE_INTERVAL_SEC", 0.01)

    with patch("soniox.realtime.stt.sync_ws_connect", return_value=ws):
        with client.realtime.stt.connect(config=CONFIG) as session:
            session.pause()
            time.sleep(0.1)
            session.resume()

    keepalives = [m for m in ws.sent_messages if m == {"type": "keepalive"}]
    assert len(keepalives) >= 3, f"expected >=3 keepalives, got {keepalives}"


async def test_keepalive_task_fires_while_paused(
    async_client: AsyncSonioxClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    ws = AsyncMockWebSocket()
    ws.close_after_recv()
    monkeypatch.setattr("soniox.realtime.async_stt.KEEP_ALIVE_INTERVAL_SEC", 0.01)

    with patch("soniox.realtime.async_stt.async_ws_connect", return_value=ws):
        async with async_client.realtime.stt.connect(config=CONFIG) as session:
            await session.pause()
            await asyncio.sleep(0.1)
            await session.resume()

    keepalives = [m for m in ws.sent_messages if m == {"type": "keepalive"}]
    assert len(keepalives) >= 3, f"expected >=3 keepalives, got {keepalives}"


def test_keepalive_thread_stops_after_resume(
    client: SonioxClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    """After ``resume()``, no further keepalive messages should be sent."""
    ws = MockWebSocket()
    ws.close_after_recv()
    monkeypatch.setattr("soniox.realtime.stt.KEEP_ALIVE_INTERVAL_SEC", 0.01)

    with patch("soniox.realtime.stt.sync_ws_connect", return_value=ws):
        with client.realtime.stt.connect(config=CONFIG) as session:
            session.pause()
            time.sleep(0.05)
            session.resume()
            count_at_resume = sum(1 for m in ws.sent_messages if m == {"type": "keepalive"})
            time.sleep(0.05)
            count_after_resume = sum(
                1 for m in ws.sent_messages if m == {"type": "keepalive"}
            )

    assert count_after_resume == count_at_resume


def test_keepalive_thread_exits_when_callback_raises() -> None:
    """If the keepalive callback raises, the background thread must exit
    cleanly instead of looping on the exception."""
    from soniox.realtime._utils import KeepaliveThread

    calls: list[int] = []

    def _raising_callback() -> None:
        calls.append(1)
        raise RuntimeError("callback exploded")

    thread = KeepaliveThread(_raising_callback, interval=0.01)
    thread.start()
    time.sleep(0.05)
    thread.stop()

    # The loop must have broken out after the first raise - no repeated calls.
    assert len(calls) == 1
    assert not thread._thread.is_alive()  # pyright: ignore[reportPrivateUsage]


async def test_keepalive_task_exits_when_callback_raises() -> None:
    from soniox.realtime._utils import KeepaliveTask

    calls: list[int] = []

    async def _raising_callback() -> None:
        calls.append(1)
        raise RuntimeError("callback exploded")

    task = KeepaliveTask(_raising_callback, interval=0.01)
    task.start()
    await asyncio.sleep(0.05)
    await task.stop()

    assert len(calls) == 1
