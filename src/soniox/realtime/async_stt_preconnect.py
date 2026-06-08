from __future__ import annotations

import asyncio
import json
import time
from collections.abc import AsyncIterator, Awaitable, Callable
from dataclasses import dataclass
from types import TracebackType

from websockets.exceptions import ConnectionClosed

from ..errors import SonioxRealtimeError, SonioxValidationError
from ..types.realtime import RealtimeControlType, RealtimeEvent, RealtimeSTTConfig
from . import _transport
from ._utils import (
    DEFAULT_IDLE_MAX_LIFETIME_SEC,
    DEFAULT_IDLE_REFRESH_BEFORE_SEC,
    DEFAULT_STT_CONNECTION_POOL_SIZE,
    KEEP_ALIVE_INTERVAL_SEC,
    KeepaliveTask,
    ws_connect_kwargs,
)


class AsyncRealtimeSTTConnection:
    """
    A pre-established async WebSocket link to the realtime STT endpoint.

    Enter the async context manager to complete the WebSocket handshake only.
    Call :meth:`start_session` later when a client session is ready.
    """

    def __init__(
        self,
        url: str,
        api_key: str,
        *,
        connect_timeout_sec: float | None = None,
    ) -> None:
        self._url = url
        self._api_key = api_key
        self._connect_timeout_sec = connect_timeout_sec
        self._ws = None
        self._idle_keepalive: KeepaliveTask | None = None
        self._session_started = False
        self._discarded = False

    @property
    def connected(self) -> bool:
        return self._ws is not None

    async def __aenter__(self) -> AsyncRealtimeSTTConnection:
        try:
            self._ws = await _transport.async_ws_connect(
                self._url,
                **ws_connect_kwargs(self._connect_timeout_sec),
            )
        except TimeoutError as exc:
            raise SonioxRealtimeError("Connection timed out") from exc
        except Exception as exc:
            raise SonioxRealtimeError("Failed to open realtime STT connection") from exc
        return self

    async def __aexit__(
        self,
        _exc_type: type[BaseException] | None,
        _exc_value: BaseException | None,
        _traceback: TracebackType | None,
    ) -> None:
        _ = (_exc_type, _exc_value, _traceback)
        await self.close()

    async def close(self) -> None:
        """Close an idle pre-connected link (pool maintenance only)."""
        await self.stop_idle_keepalive()
        if not self._ws:
            return
        try:
            await self._ws.close()
        finally:
            self._ws = None

    async def discard(self, *, send_finish: bool = False) -> None:
        """Close a link after a session. Never returned to a pool or reused."""
        if self._discarded:
            return
        self._discarded = True
        await self.stop_idle_keepalive()
        if not self._ws:
            return
        if send_finish:
            try:
                await self._send_empty()
            except ConnectionClosed:
                pass
            except SonioxRealtimeError:
                pass
        try:
            await self._ws.close()
        finally:
            self._ws = None

    async def keep_alive(self) -> None:
        await self._send_json({"type": "keepalive"})

    async def start_idle_keepalive(
        self,
        *,
        interval_sec: float = KEEP_ALIVE_INTERVAL_SEC,
    ) -> None:
        if not self._ws:
            raise SonioxRealtimeError("Realtime STT connection is not open")
        if self._session_started:
            raise SonioxRealtimeError("Cannot start idle keepalive after a session has started")
        if interval_sec <= 0:
            raise SonioxValidationError("keepalive interval must be greater than 0")
        if self._idle_keepalive is not None:
            return
        self._idle_keepalive = KeepaliveTask(self.keep_alive, interval_sec)
        self._idle_keepalive.start()

    async def stop_idle_keepalive(self) -> None:
        if self._idle_keepalive is not None:
            await self._idle_keepalive.stop()
            self._idle_keepalive = None

    async def start_session(
        self,
        *,
        config: RealtimeSTTConfig,
        api_key: str | None = None,
    ) -> AsyncRealtimeSTTStream:
        if self._discarded:
            raise SonioxRealtimeError("This connection has already been discarded")
        if not self._ws:
            raise SonioxRealtimeError("Realtime STT connection is not open")
        if self._session_started:
            raise SonioxRealtimeError("This connection already has an active session")
        await self.stop_idle_keepalive()
        key = api_key or self._api_key
        payload = config.build_payload(key)
        try:
            await self._ws.send(json.dumps(payload.model_dump(exclude_none=True)))
        except Exception as exc:
            raise SonioxRealtimeError("Failed to start realtime STT session") from exc
        self._session_started = True
        return AsyncRealtimeSTTStream(self, payload)

    async def _send_json(self, payload: dict[str, object]) -> None:
        if not self._ws:
            raise SonioxRealtimeError("Realtime STT connection is not open")
        try:
            await self._ws.send(json.dumps(payload))
        except Exception as exc:
            raise SonioxRealtimeError("Failed to send STT control message") from exc

    async def _send_bytes(self, chunk: bytes) -> None:
        if not self._ws:
            raise SonioxRealtimeError("Realtime STT connection is not open")
        try:
            await self._ws.send(chunk)
        except Exception as exc:
            raise SonioxRealtimeError("Failed to send audio chunk") from exc

    async def _send_empty(self) -> None:
        if not self._ws:
            raise SonioxRealtimeError("Realtime STT connection is not open")
        try:
            await self._ws.send("")
        except Exception as exc:
            raise SonioxRealtimeError("Failed to send control message") from exc

    async def _recv_bytes(self) -> bytes:
        if not self._ws:
            raise SonioxRealtimeError("Realtime STT connection is not open")
        try:
            message = await self._ws.recv()
        except ConnectionClosed:
            self._ws = None
            return b""
        if isinstance(message, str):
            return message.encode("utf-8")
        return message


class AsyncRealtimeSTTStream:
    """An active async realtime STT session on a pre-connected link."""

    def __init__(
        self,
        connection: AsyncRealtimeSTTConnection,
        config: RealtimeSTTConfig,
    ) -> None:
        self._connection = connection
        self._config = config
        self._last_message: RealtimeEvent | None = None
        self._paused = False
        self._keepalive: KeepaliveTask | None = None
        self._finish_sent = False
        self._finish_sent = False

    @property
    def config(self) -> RealtimeSTTConfig:
        return self._config

    @property
    def paused(self) -> bool:
        return self._paused

    @property
    def last_message(self) -> RealtimeEvent | None:
        return self._last_message

    async def send_byte_chunk(self, chunk: bytes) -> None:
        if self._paused:
            return
        await self._connection._send_bytes(chunk)

    async def send_bytes(
        self, chunks: bytes | AsyncIterator[bytes], *, finish: bool = True
    ) -> None:
        if isinstance(chunks, bytes):
            await self.send_byte_chunk(chunks)
            return
        async for chunk in chunks:
            await self.send_byte_chunk(chunk)
        if finish:
            await self.finish()

    async def send_control_message(self, control_type: RealtimeControlType) -> None:
        if control_type == RealtimeControlType.FINISH:
            await self._connection._send_empty()
        elif control_type == RealtimeControlType.KEEP_ALIVE:
            await self._connection._send_json({"type": "keepalive"})
        elif control_type == RealtimeControlType.FINALIZE:
            await self._connection._send_json({"type": "finalize"})

    async def finish(self) -> None:
        self._finish_sent = True
        await self.send_control_message(RealtimeControlType.FINISH)

    async def keep_alive(self) -> None:
        await self.send_control_message(RealtimeControlType.KEEP_ALIVE)

    async def finalize(self) -> None:
        await self.send_control_message(RealtimeControlType.FINALIZE)

    async def recv_bytes(self) -> bytes:
        return await self._connection._recv_bytes()

    def parse_event(self, raw: str | bytes) -> RealtimeEvent:
        return RealtimeEvent.validate_event(raw)

    async def receive_event(self) -> RealtimeEvent | None:
        raw = await self.recv_bytes()
        if not raw:
            return None
        event = self.parse_event(raw)
        self._last_message = event
        return event

    async def receive_events(self) -> AsyncIterator[RealtimeEvent]:
        while True:
            event = await self.receive_event()
            if event is None:
                break
            yield event

    async def handle_events(
        self, handler: Callable[[RealtimeEvent], Awaitable[None]]
    ) -> None:
        async for event in self.receive_events():
            await handler(event)

    async def pause(self, *, finalize: bool = True) -> None:
        if self._paused:
            return
        if finalize:
            await self.finalize()
        self._paused = True
        self._keepalive = KeepaliveTask(self.keep_alive, KEEP_ALIVE_INTERVAL_SEC)
        self._keepalive.start()

    async def resume(self) -> None:
        if not self._paused:
            return
        if self._keepalive is not None:
            await self._keepalive.stop()
            self._keepalive = None
        self._paused = False

    async def close(self) -> None:
        """Discard the session link. It is never returned to a pool."""
        if self._keepalive is not None:
            await self._keepalive.stop()
            self._keepalive = None
        self._paused = False
        await self._connection.discard(send_finish=not self._finish_sent)


class AsyncRealtimeSTTPooledSession:
    """Async realtime STT session backed by the internal connection pool."""

    def __init__(
        self,
        pool: AsyncRealtimeSTTConnectionPool,
        config: RealtimeSTTConfig,
        *,
        api_key: str | None = None,
    ) -> None:
        self._pool = pool
        self._config = config
        self._api_key = api_key
        self._stream: AsyncRealtimeSTTStream | None = None

    @property
    def config(self) -> RealtimeSTTConfig:
        if self._stream is not None:
            return self._stream.config
        return self._config

    @property
    def paused(self) -> bool:
        return self._stream.paused if self._stream is not None else False

    @property
    def last_message(self) -> RealtimeEvent | None:
        return self._stream.last_message if self._stream is not None else None

    async def __aenter__(self) -> AsyncRealtimeSTTPooledSession:
        await self._pool.warmup()
        self._stream = await self._pool.start_session(config=self._config, api_key=self._api_key)
        return self

    async def __aexit__(
        self,
        _exc_type: type[BaseException] | None,
        _exc_value: BaseException | None,
        _traceback: TracebackType | None,
    ) -> None:
        _ = (_exc_type, _exc_value, _traceback)
        await self.close()

    async def close(self) -> None:
        if self._stream is not None:
            await self._stream.close()
            self._stream = None

    def _require_stream(self) -> AsyncRealtimeSTTStream:
        if self._stream is None:
            raise SonioxRealtimeError("Realtime session is not connected")
        return self._stream

    async def send_byte_chunk(self, chunk: bytes) -> None:
        await self._require_stream().send_byte_chunk(chunk)

    async def send_bytes(
        self, chunks: bytes | AsyncIterator[bytes], *, finish: bool = True
    ) -> None:
        await self._require_stream().send_bytes(chunks, finish=finish)

    async def send_control_message(self, control_type: RealtimeControlType) -> None:
        await self._require_stream().send_control_message(control_type)

    async def finish(self) -> None:
        await self._require_stream().finish()

    async def keep_alive(self) -> None:
        await self._require_stream().keep_alive()

    async def finalize(self) -> None:
        await self._require_stream().finalize()

    async def recv_bytes(self) -> bytes:
        return await self._require_stream().recv_bytes()

    def parse_event(self, raw: str | bytes) -> RealtimeEvent:
        return self._require_stream().parse_event(raw)

    async def receive_event(self) -> RealtimeEvent | None:
        return await self._require_stream().receive_event()

    async def receive_events(self) -> AsyncIterator[RealtimeEvent]:
        stream = self._require_stream()
        async for event in stream.receive_events():
            yield event

    async def handle_events(
        self, handler: Callable[[RealtimeEvent], Awaitable[None]]
    ) -> None:
        await self._require_stream().handle_events(handler)

    async def pause(self, *, finalize: bool = True) -> None:
        await self._require_stream().pause(finalize=finalize)

    async def resume(self) -> None:
        await self._require_stream().resume()

    enter = __aenter__
    aenter = __aenter__


@dataclass
class _AsyncPooledIdleLink:
    conn: AsyncRealtimeSTTConnection
    opened_at: float

    def age_sec(self) -> float:
        return time.monotonic() - self.opened_at

    def is_expired(self, max_lifetime_sec: float) -> bool:
        return self.age_sec() >= max_lifetime_sec

    def should_refresh(self, max_lifetime_sec: float, refresh_before_sec: float) -> bool:
        remaining = max_lifetime_sec - self.age_sec()
        return remaining <= refresh_before_sec


class AsyncRealtimeSTTConnectionPool:
    """
    Async pool of idle WebSocket links to the realtime STT endpoint.

    Callers **borrow** with :meth:`borrow_connection`: the link leaves the
    pool immediately; if none is idle, a new WebSocket opens synchronously.
    The pool refills in the background. Session links are discarded, never reused.
    """

    def __init__(
        self,
        *,
        url: str,
        api_key: str,
        pool_size: int = DEFAULT_STT_CONNECTION_POOL_SIZE,
        connect_timeout_sec: float | None = None,
        idle_keepalive: bool = True,
        keepalive_interval_sec: float = KEEP_ALIVE_INTERVAL_SEC,
        idle_max_lifetime_sec: float = DEFAULT_IDLE_MAX_LIFETIME_SEC,
        idle_refresh_before_sec: float = DEFAULT_IDLE_REFRESH_BEFORE_SEC,
    ) -> None:
        if pool_size < 1:
            raise SonioxValidationError("pool_size must be at least 1")
        if keepalive_interval_sec <= 0:
            raise SonioxValidationError("keepalive_interval_sec must be greater than 0")
        if idle_max_lifetime_sec <= 0:
            raise SonioxValidationError("idle_max_lifetime_sec must be greater than 0")
        if idle_refresh_before_sec <= 0:
            raise SonioxValidationError("idle_refresh_before_sec must be greater than 0")
        if idle_refresh_before_sec >= idle_max_lifetime_sec:
            raise SonioxValidationError(
                "idle_refresh_before_sec must be less than idle_max_lifetime_sec"
            )
        self._url = url
        self._api_key = api_key
        self._pool_size = pool_size
        self._connect_timeout_sec = connect_timeout_sec
        self._idle_keepalive = idle_keepalive
        self._keepalive_interval_sec = keepalive_interval_sec
        self._idle_max_lifetime_sec = idle_max_lifetime_sec
        self._idle_refresh_before_sec = idle_refresh_before_sec
        self._idle: asyncio.Queue[_AsyncPooledIdleLink] = asyncio.Queue()
        self._closed = False
        self._replenish_lock = asyncio.Lock()
        self._maintenance: KeepaliveTask | None = None

    async def __aenter__(self) -> AsyncRealtimeSTTConnectionPool:
        await self.warmup()
        return self

    async def __aexit__(
        self,
        _exc_type: type[BaseException] | None,
        _exc_value: BaseException | None,
        _traceback: TracebackType | None,
    ) -> None:
        _ = (_exc_type, _exc_value, _traceback)
        await self.close()

    @property
    def idle_count(self) -> int:
        return self._idle.qsize()

    async def borrow_connection(self) -> AsyncRealtimeSTTConnection:
        """
        Borrow an idle link from the pool.

        The link is removed from the pool. If none is idle, opens a new
        WebSocket immediately. The pool refills in the background afterward.
        """
        if self._closed:
            raise SonioxRealtimeError("Connection pool is closed")
        conn = await self._borrow_connection()
        asyncio.create_task(self._replenish_one(), name="soniox-stt-pool-replenish")
        return conn

    async def warmup(self) -> None:
        if self._closed:
            raise SonioxRealtimeError("Preconnect pool is closed")
        self._start_maintenance()
        while self._idle.qsize() < self._pool_size:
            await self._idle.put(await self._open_idle_link())

    async def start_session(
        self,
        *,
        config: RealtimeSTTConfig,
        api_key: str | None = None,
    ) -> AsyncRealtimeSTTStream:
        conn = await self.borrow_connection()
        try:
            return await conn.start_session(config=config, api_key=api_key)
        except Exception:
            await conn.discard()
            raise

    async def close(self) -> None:
        self._closed = True
        if self._maintenance is not None:
            await self._maintenance.stop()
            self._maintenance = None
        while not self._idle.empty():
            link = await self._idle.get()
            await link.conn.close()

    def _start_maintenance(self) -> None:
        if self._maintenance is not None:
            return
        self._maintenance = KeepaliveTask(
            self._maintain_idle_links,
            self._keepalive_interval_sec,
        )
        self._maintenance.start()

    async def _open_idle_link(self) -> _AsyncPooledIdleLink:
        conn = AsyncRealtimeSTTConnection(
            self._url,
            self._api_key,
            connect_timeout_sec=self._connect_timeout_sec,
        )
        await conn.__aenter__()
        if self._idle_keepalive:
            await conn.start_idle_keepalive(interval_sec=self._keepalive_interval_sec)
        return _AsyncPooledIdleLink(conn=conn, opened_at=time.monotonic())

    async def _borrow_connection(self) -> AsyncRealtimeSTTConnection:
        """Take one link out of the idle queue, or open a new one if empty."""
        while not self._closed:
            try:
                link = self._idle.get_nowait()
            except asyncio.QueueEmpty:
                return (await self._open_idle_link()).conn
            if link.is_expired(self._idle_max_lifetime_sec):
                await link.conn.close()
                continue
            if link.should_refresh(
                self._idle_max_lifetime_sec,
                self._idle_refresh_before_sec,
            ):
                await link.conn.close()
                return (await self._open_idle_link()).conn
            return link.conn
        raise SonioxRealtimeError("Connection pool is closed")

    async def _maintain_idle_links(self) -> None:
        if self._closed:
            return
        async with self._replenish_lock:
            if self._closed:
                return
            kept: list[_AsyncPooledIdleLink] = []
            while not self._idle.empty():
                link = self._idle.get_nowait()
                if link.is_expired(self._idle_max_lifetime_sec) or link.should_refresh(
                    self._idle_max_lifetime_sec,
                    self._idle_refresh_before_sec,
                ):
                    await link.conn.close()
                else:
                    kept.append(link)
            for link in kept:
                await self._idle.put(link)
            while self._idle.qsize() < self._pool_size:
                try:
                    await self._idle.put(await self._open_idle_link())
                except Exception:
                    break

    async def _replenish_one(self) -> None:
        if self._closed:
            return
        async with self._replenish_lock:
            if self._closed or self._idle.qsize() >= self._pool_size:
                return
            try:
                await self._idle.put(await self._open_idle_link())
            except Exception:
                return


AsyncRealtimeSTTPreconnectPool = AsyncRealtimeSTTConnectionPool
