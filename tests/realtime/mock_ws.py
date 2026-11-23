"""
Deterministic fake WebSocket implementations for realtime SDK tests.

Usage:
    ws = MockWebSocket()
    ws.push_recv({"tokens": [...]})    # queue a normal JSON event
    ws.push_recv_raw("not-json")       # queue a raw string/bytes message
    ws.push_recv_error(ConnectionClosed(None, None))  # raise from the next recv()
    ws.close_after_recv()              # raise ConnectionClosedOK from the next recv()

    # After the SDK runs, inspect:
    ws.sent_messages       # parsed JSON dicts or raw bytes, in order
    ws.closed              # True if the SDK (or the mock) closed the socket
    ws.aborted             # True if it was abandoned instead of closed

A script that runs out is a broken script, not the end of a stream: the server
ends one with a terminal frame (`finished` or an `error_code`) and only then
closes. Say both, or the mock fails the test where it ran out.

The async variant mirrors the API and implements ``__await__`` so it can be
returned directly from ``async_ws_connect`` patches.
"""

from __future__ import annotations

import asyncio
import json
import queue
import time
from typing import Any

from websockets.exceptions import ConnectionClosed, ConnectionClosedOK

_EOF = object()  # sentinel: recv() raises ConnectionClosedOK when popped
_SILENT = object()  # sentinel: recv() times out, as a silently dropped socket does
_RAN_OUT = "the mock script ran out; end it with a terminal frame and close_after_recv()"


class _BaseMockWebSocket:
    def __init__(self) -> None:
        self.sent_messages: list[Any] = []
        self.closed: bool = False
        self.aborted: bool = False
        self.ended_by_us: int = 0
        """Closes the session asked for, which is what ends the stream server-side."""

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

    def go_silent(self) -> None:
        """Nothing arrives and nothing closes, as when the network drops the socket."""
        self._queue.put(_SILENT)

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
            item = self._queue.get_nowait()
        except queue.Empty:
            raise AssertionError(_RAN_OUT) from None
        if item is _EOF:
            self.closed = True
            raise ConnectionClosedOK(None, None)
        if item is _SILENT:
            self._queue.put(_SILENT)
            time.sleep(min(wait, 0.01))
            raise TimeoutError
        if isinstance(item, BaseException):
            # Only a connection error leaves the socket unusable. A real
            # `recv` that times out leaves it open, which is what a test about
            # abandoning one has to be able to see.
            if isinstance(item, ConnectionClosed):
                self.closed = True
            raise item
        if isinstance(item, (dict, list)):
            return json.dumps(item)
        return item

    def close(self) -> None:
        self.closed = True
        self.ended_by_us += 1

    def close_socket(self) -> None:
        """Abandon the connection without a close frame, as a reconnect does."""
        self.closed = True
        self.aborted = True


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

    def go_silent(self) -> None:
        """Say nothing from here on, as a silently dropped socket does."""
        self._queue.put_nowait(_SILENT)

    # --- websocket-like API -------------------------------------------------

    async def send(self, message: str | bytes) -> None:
        if self.closed:
            raise ConnectionClosed(None, None)
        self._record_send(message)

    async def recv(self, timeout: float | None = None) -> str | bytes:
        _ = timeout  # The session bounds its own wait.
        if self.closed:
            raise ConnectionClosed(None, None)
        try:
            item = self._queue.get_nowait()
        except asyncio.QueueEmpty:
            raise AssertionError(_RAN_OUT) from None
        if item is _SILENT:
            # Nothing arrives and nothing is raised: the session's own wait is
            # what notices, through the ping that went unanswered.
            self._queue.put_nowait(_SILENT)
            await asyncio.Event().wait()
        if item is _EOF:
            self.closed = True
            raise ConnectionClosedOK(None, None)
        if isinstance(item, BaseException):
            # Only a connection error leaves the socket unusable. A real
            # `recv` that times out leaves it open, which is what a test about
            # abandoning one has to be able to see.
            if isinstance(item, ConnectionClosed):
                self.closed = True
            raise item
        if isinstance(item, (dict, list)):
            return json.dumps(item)
        return item

    async def close(self) -> None:
        self.closed = True
        self.ended_by_us += 1

    @property
    def transport(self) -> Any:
        """Stands in for the asyncio transport a reconnect aborts."""
        mock = self

        class _Transport:
            def abort(self) -> None:
                mock.closed = True
                mock.aborted = True

        return _Transport()

    def __await__(self):
        # Lets the mock stand in for `await async_ws_connect(url)`.
        async def _return_self() -> AsyncMockWebSocket:
            return self

        return _return_self().__await__()
