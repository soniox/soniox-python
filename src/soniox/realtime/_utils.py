from __future__ import annotations

import asyncio
import threading
from collections.abc import Awaitable, Callable

from ..errors import SonioxValidationError

KEEP_ALIVE_INTERVAL_SEC: float = 5.0
DEFAULT_CONNECT_TIMEOUT_SEC: float = 10.0


def validate_connect_timeout_sec(timeout_sec: float) -> float:
    """Validate a realtime WebSocket connect timeout."""
    if timeout_sec <= 0:
        raise SonioxValidationError("connect_timeout_sec must be greater than zero")
    return timeout_sec


class KeepaliveThread:
    """
    Background thread that periodically invokes a callback until stopped.
    """

    def __init__(self, callback: Callable[[], None], interval: float) -> None:
        """
        Args:
            callback:
                Callable invoked on each tick. If it raises, the loop exits.
            interval:
                Seconds between ticks.
        """
        self._callback = callback
        self._interval = interval
        self._stop_event = threading.Event()
        self._thread = threading.Thread(
            target=self._loop,
            name="soniox-keepalive",
            daemon=True,
        )

    def start(self) -> None:
        """Start the background thread."""
        self._thread.start()

    def stop(self) -> None:
        """Signal the thread to stop and block until it exits."""
        self._stop_event.set()
        self._thread.join()

    def _loop(self) -> None:
        while not self._stop_event.wait(timeout=self._interval):
            try:
                self._callback()
            except Exception:
                break


class KeepaliveTask:
    """
    Async background task that periodically invokes a callback until stopped.
    """

    def __init__(self, callback: Callable[[], Awaitable[None]], interval: float) -> None:
        """
        Args:
            callback:
                Coroutine function invoked on each tick. If it raises, the loop exits.
            interval:
                Seconds between ticks.
        """
        self._callback = callback
        self._interval = interval
        self._stop_event = asyncio.Event()
        self._task: asyncio.Task[None] | None = None

    def start(self) -> None:
        """Schedule the background task on the running event loop."""
        self._task = asyncio.create_task(self._loop(), name="soniox-keepalive")

    async def stop(self) -> None:
        """Signal the task to stop and wait for it to finish."""
        self._stop_event.set()
        if self._task is not None:
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None

    async def _loop(self) -> None:
        while True:
            try:
                await asyncio.wait_for(
                    asyncio.shield(self._stop_event.wait()),
                    timeout=self._interval,
                )
                break
            except asyncio.TimeoutError:
                pass
            try:
                await self._callback()
            except Exception:
                break
