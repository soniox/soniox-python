"""
Deterministic fake WebSocket implementations for realtime SDK tests.

Usage:
    ws = MockWebSocket()
    ws.push_recv({"tokens": [...]})    # queue a normal JSON event
    ws.push_recv_raw("not-json")       # queue a raw string/bytes message
    ws.push_recv_error(ConnectionClosed(None, None))  # raise from the next recv()
    ws.close_after_recv()              # raise ConnectionClosed from the next recv()

    # After the SDK runs, inspect:
    ws.sent_messages       # parsed JSON dicts or raw bytes, in order
    ws.closed              # True if the SDK (or the mock) closed the socket

The async variant mirrors the API and implements ``__await__`` so it can be
returned directly from ``async_ws_connect`` patches.
"""

from __future__ import annotations

import asyncio
import json
import queue
from typing import Any

from websockets.exceptions import ConnectionClosed

_EOF = object()  # sentinel: recv() raises ConnectionClosed when popped


class _BaseMockWebSocket:
    def __init__(self) -> None:
        self.sent_messages: list[Any] = []
        self.closed: bool = False

    def _record_send(self, message: str | bytes) -> None:
        if isinstance(message, str) and message:
            try:
                self.sent_messages.append(json.loads(message))
                return
            except json.JSONDecodeError:
                pass
        self.sent_messages.append(message)


class MockWebSocket(_BaseMockWebSocket):
    def __init__(self) -> None:
        super().__init__()
        self._queue: queue.Queue[Any] = queue.Queue()

    # --- programming API ----------------------------------------------------

    def push_recv(self, payload: dict) -> None:
        self._queue.put(payload)

    def push_recv_raw(self, raw: str | bytes) -> None:
        self._queue.put(raw)

    def push_recv_error(self, exc: BaseException) -> None:
        self._queue.put(exc)

    def close_after_recv(self) -> None:
        self._queue.put(_EOF)

    # --- websocket-like API -------------------------------------------------

    def send(self, message: str | bytes) -> None:
        if self.closed:
            raise ConnectionClosed(None, None)
        self._record_send(message)

    def recv(self, timeout: float | None = None) -> str | bytes:
        if self.closed:
            raise ConnectionClosed(None, None)
        wait = timeout if timeout is not None else 0.5
        try:
            item = self._queue.get(timeout=wait)
        except queue.Empty:
            self.closed = True
            raise ConnectionClosed(None, None) from None
        if item is _EOF:
            self.closed = True
            raise ConnectionClosed(None, None)
        if isinstance(item, BaseException):
            self.closed = True
            raise item
        if isinstance(item, (dict, list)):
            return json.dumps(item)
        return item

    def close(self) -> None:
        self.closed = True


class AsyncMockWebSocket(_BaseMockWebSocket):
    def __init__(self) -> None:
        super().__init__()
        self._queue: asyncio.Queue[Any] = asyncio.Queue()

    # --- programming API (sync; the queue is filled before the test runs) --

    def push_recv(self, payload: dict) -> None:
        self._queue.put_nowait(payload)

    def push_recv_raw(self, raw: str | bytes) -> None:
        self._queue.put_nowait(raw)

    def push_recv_error(self, exc: BaseException) -> None:
        self._queue.put_nowait(exc)

    def close_after_recv(self) -> None:
        self._queue.put_nowait(_EOF)

    # --- websocket-like API -------------------------------------------------

    async def send(self, message: str | bytes) -> None:
        if self.closed:
            raise ConnectionClosed(None, None)
        self._record_send(message)

    async def recv(self, timeout: float | None = None) -> str | bytes:
        if self.closed:
            raise ConnectionClosed(None, None)
        wait = timeout if timeout is not None else 0.5
        try:
            item = await asyncio.wait_for(self._queue.get(), timeout=wait)
        except asyncio.TimeoutError:
            self.closed = True
            raise ConnectionClosed(None, None) from None
        if item is _EOF:
            self.closed = True
            raise ConnectionClosed(None, None)
        if isinstance(item, BaseException):
            self.closed = True
            raise item
        if isinstance(item, (dict, list)):
            return json.dumps(item)
        return item

    async def close(self) -> None:
        self.closed = True

    def __await__(self):
        # Lets the mock stand in for `await async_ws_connect(url)`.
        async def _return_self() -> AsyncMockWebSocket:
            return self

        return _return_self().__await__()
