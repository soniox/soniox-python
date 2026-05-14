"""
Realtime tests against a real local WebSocket server.

These tests run the actual :class:`RealtimeSTTSession` / async counterpart
against a ``websockets`` server bound to ``127.0.0.1:0`` - no mocking of
``sync_ws_connect`` or ``async_ws_connect``. They catch anything a mock can't:
real connect/close handshakes, event-loop integration, socket-level EOF
semantics, and the async keepalive task running against a real socket.

Tests are marked ``live_ws`` so they can be excluded from fast runs via
``pytest -m "not live_ws"``.
"""

from __future__ import annotations

import asyncio
import json
import threading
from collections.abc import AsyncIterator, Awaitable, Callable, Iterator
from dataclasses import dataclass, field
from typing import Any

import pytest
from websockets.asyncio.server import ServerConnection as AsyncServerConnection
from websockets.asyncio.server import serve as async_serve
from websockets.sync.server import ServerConnection as SyncServerConnection
from websockets.sync.server import serve as sync_serve

from soniox.client import AsyncSonioxClient, SonioxClient
from soniox.types.realtime import RealtimeSTTConfig

pytestmark = [pytest.mark.live_ws, pytest.mark.timeout(15)]

CONFIG = RealtimeSTTConfig(model="v1")


# ---------------------------------------------------------------------------
# Shared recording structure
# ---------------------------------------------------------------------------


@dataclass
class ServerLog:
    """Everything the server handler observed during a test."""

    config: dict[str, Any] | None = None
    received: list[Any] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Sync server fixture
# ---------------------------------------------------------------------------


SyncHandler = Callable[[SyncServerConnection], None]


def _default_sync_handler(log: ServerLog) -> SyncHandler:
    """Minimal Soniox protocol emulator: read config + frames, send two events."""

    def handler(ws: SyncServerConnection) -> None:
        raw = ws.recv()
        log.config = json.loads(raw)
        while True:
            try:
                msg = ws.recv()
            except Exception:
                return
            if isinstance(msg, bytes):
                log.received.append(msg)
            elif msg == "":
                # FINISH
                break
            else:
                log.received.append(json.loads(msg))
        ws.send(json.dumps({"tokens": [{"text": "hi", "is_final": True}]}))
        ws.send(json.dumps({"tokens": [], "finished": True}))

    return handler


@pytest.fixture
def sync_ws_url_and_log() -> Iterator[tuple[str, ServerLog]]:
    """Spin up a sync websockets server on 127.0.0.1:0 for the duration of the test."""
    log = ServerLog()
    handler = _default_sync_handler(log)

    server = sync_serve(handler, "127.0.0.1", 0)
    port = server.socket.getsockname()[1]
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"ws://127.0.0.1:{port}", log
    finally:
        server.shutdown()
        thread.join(timeout=5)


# ---------------------------------------------------------------------------
# Async server fixture
# ---------------------------------------------------------------------------


AsyncHandler = Callable[[AsyncServerConnection], Awaitable[None]]


def _default_async_handler(log: ServerLog) -> AsyncHandler:
    async def handler(ws: AsyncServerConnection) -> None:
        raw = await ws.recv()
        log.config = json.loads(raw)
        while True:
            try:
                msg = await ws.recv()
            except Exception:
                return
            if isinstance(msg, bytes):
                log.received.append(msg)
            elif msg == "":
                break
            else:
                log.received.append(json.loads(msg))
        await ws.send(json.dumps({"tokens": [{"text": "hi", "is_final": True}]}))
        await ws.send(json.dumps({"tokens": [], "finished": True}))

    return handler


@pytest.fixture
async def async_ws_url_and_log() -> AsyncIterator[tuple[str, ServerLog]]:
    log = ServerLog()
    handler = _default_async_handler(log)

    async with async_serve(handler, "127.0.0.1", 0, ping_interval=None) as server:
        port = server.sockets[0].getsockname()[1]
        yield f"ws://127.0.0.1:{port}", log


# ---------------------------------------------------------------------------
# 1. Sync happy path
# ---------------------------------------------------------------------------


def test_sync_happy_path(sync_ws_url_and_log: tuple[str, ServerLog]) -> None:
    url, _ = sync_ws_url_and_log
    with SonioxClient(api_key="test_key", websocket_base_url=url) as client:
        with client.realtime.stt.connect(config=CONFIG) as session:
            session.send_byte_chunk(b"audio-bytes")
            session.finish()
            events = list(session.receive_events())

    assert len(events) == 2
    assert events[0].tokens[0].text == "hi"
    assert events[1].finished is True


# ---------------------------------------------------------------------------
# 2. Async happy path
# ---------------------------------------------------------------------------


async def test_async_happy_path(async_ws_url_and_log: tuple[str, ServerLog]) -> None:
    url, _ = async_ws_url_and_log
    async with AsyncSonioxClient(api_key="test_key", websocket_base_url=url) as client:
        async with client.realtime.stt.connect(config=CONFIG) as session:
            await session.send_byte_chunk(b"audio-bytes")
            await session.finish()
            events = [event async for event in session.receive_events()]

    assert len(events) == 2
    assert events[0].tokens[0].text == "hi"
    assert events[1].finished is True


# ---------------------------------------------------------------------------
# 3. Server-initiated close → treated as EOF, not raised
# ---------------------------------------------------------------------------


def test_sync_server_closes_immediately_is_treated_as_eof() -> None:
    def handler(ws: SyncServerConnection) -> None:
        ws.recv()  # read config
        # Return immediately -- triggers a clean close.

    server = sync_serve(handler, "127.0.0.1", 0)
    port = server.socket.getsockname()[1]
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        with SonioxClient(
            api_key="test_key", websocket_base_url=f"ws://127.0.0.1:{port}"
        ) as client:
            with client.realtime.stt.connect(config=CONFIG) as session:
                events = list(session.receive_events())
        assert events == []
    finally:
        server.shutdown()
        thread.join(timeout=5)


# ---------------------------------------------------------------------------
# 4. Config round-trip - SDK must serialize what we expect the server to see
# ---------------------------------------------------------------------------


def test_sync_config_round_trip(sync_ws_url_and_log: tuple[str, ServerLog]) -> None:
    url, log = sync_ws_url_and_log
    config = RealtimeSTTConfig(
        model="stt-rt-v3",
        audio_format="pcm_s16le",
        sample_rate=16000,
        num_channels=1,
        language_hints=["en"],
    )
    with SonioxClient(api_key="test_key", websocket_base_url=url) as client:
        with client.realtime.stt.connect(config=config) as session:
            session.finish()
            list(session.receive_events())

    assert log.config is not None
    assert log.config["model"] == "stt-rt-v3"
    assert log.config["audio_format"] == "pcm_s16le"
    assert log.config["sample_rate"] == 16000
    assert log.config["num_channels"] == 1
    assert log.config["language_hints"] == ["en"]
    assert log.config["api_key"] == "test_key"


# ---------------------------------------------------------------------------
# 5. Pause → keepalive actually reaches the server
# ---------------------------------------------------------------------------


async def test_async_keepalive_reaches_server(monkeypatch: pytest.MonkeyPatch) -> None:
    """The async keepalive task, running against a real socket and event loop,
    must actually deliver keepalive messages to the server."""
    monkeypatch.setattr("soniox.realtime.async_stt.KEEP_ALIVE_INTERVAL_SEC", 0.02)

    log = ServerLog()

    async def handler(ws: AsyncServerConnection) -> None:
        raw = await ws.recv()
        log.config = json.loads(raw)
        try:
            while True:
                msg = await ws.recv()
                if isinstance(msg, bytes):
                    log.received.append(msg)
                elif msg == "":
                    break
                else:
                    log.received.append(json.loads(msg))
        except Exception:
            return

    async with async_serve(handler, "127.0.0.1", 0, ping_interval=None) as server:
        port = server.sockets[0].getsockname()[1]
        url = f"ws://127.0.0.1:{port}"

        async with AsyncSonioxClient(api_key="test_key", websocket_base_url=url) as client:
            async with client.realtime.stt.connect(config=CONFIG) as session:
                await session.pause()
                await asyncio.sleep(0.15)
                await session.resume()
                await session.finish()

    keepalives = [m for m in log.received if m == {"type": "keepalive"}]
    assert len(keepalives) >= 2, f"expected >=2 keepalives, got {log.received}"
