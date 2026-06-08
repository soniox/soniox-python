from __future__ import annotations

import json
import queue
import threading
import time
from collections.abc import Callable, Iterator
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
    KeepaliveThread,
    ws_connect_kwargs,
)


class RealtimeSTTConnection:
    """
    A pre-established WebSocket link to the realtime STT endpoint.

    Enter the context manager to complete the WebSocket handshake only.
    Call :meth:`start_session` later when a client session is ready; that
    sends the config JSON and returns a :class:`RealtimeSTTStream`.

    While idle (connected but no session started), call
    :meth:`start_idle_keepalive` to send periodic keepalive messages.
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
        self._idle_keepalive: KeepaliveThread | None = None
        self._session_started = False
        self._discarded = False

    @property
    def connected(self) -> bool:
        """Return True when the WebSocket handshake has completed."""
        return self._ws is not None

    def __enter__(self) -> RealtimeSTTConnection:
        try:
            self._ws = _transport.sync_ws_connect(
                self._url,
                **ws_connect_kwargs(self._connect_timeout_sec),
            )
        except TimeoutError as exc:
            raise SonioxRealtimeError("Connection timed out") from exc
        except Exception as exc:
            raise SonioxRealtimeError("Failed to open realtime STT connection") from exc
        return self

    def __exit__(
        self,
        _exc_type: type[BaseException] | None,
        _exc_value: BaseException | None,
        _traceback: TracebackType | None,
    ) -> None:
        _ = (_exc_type, _exc_value, _traceback)
        self.close()

    def close(self) -> None:
        """Close an idle pre-connected link (pool maintenance only)."""
        self.stop_idle_keepalive()
        if not self._ws:
            return
        try:
            self._ws.close()
        finally:
            self._ws = None

    def discard(self, *, send_finish: bool = False) -> None:
        """
        Close a link after a transcription session ends.

        The WebSocket is closed and never returned to a connection pool or
        reused for another session.
        """
        if self._discarded:
            return
        self._discarded = True
        self.stop_idle_keepalive()
        if not self._ws:
            return
        if send_finish:
            try:
                self._send_empty()
            except ConnectionClosed:
                pass
            except SonioxRealtimeError:
                pass
        try:
            self._ws.close()
        finally:
            self._ws = None

    def keep_alive(self) -> None:
        """Send a keepalive control message on the open WebSocket."""
        self._send_json({"type": "keepalive"})

    def start_idle_keepalive(
        self,
        *,
        interval_sec: float = KEEP_ALIVE_INTERVAL_SEC,
    ) -> None:
        """
        Start a background thread that sends keepalive messages while idle.

        Only valid before :meth:`start_session` is called. Calling
        :meth:`start_session` stops the idle keepalive automatically.
        """
        if not self._ws:
            raise SonioxRealtimeError("Realtime STT connection is not open")
        if self._session_started:
            raise SonioxRealtimeError("Cannot start idle keepalive after a session has started")
        if interval_sec <= 0:
            raise SonioxValidationError("keepalive interval must be greater than 0")
        if self._idle_keepalive is not None:
            return
        self._idle_keepalive = KeepaliveThread(self.keep_alive, interval_sec)
        self._idle_keepalive.start()

    def stop_idle_keepalive(self) -> None:
        """Stop the background idle keepalive thread, if running."""
        if self._idle_keepalive is not None:
            self._idle_keepalive.stop()
            self._idle_keepalive = None

    def start_session(
        self,
        *,
        config: RealtimeSTTConfig,
        api_key: str | None = None,
    ) -> RealtimeSTTStream:
        """
        Start a transcription session on this pre-connected WebSocket.

        Sends the session config as the first application message, then
        returns a stream handle for audio and events.

        Each connection supports at most one session. After the session
        ends, call :meth:`RealtimeSTTStream.close` to discard the link; it
        is never reused.
        """
        if self._discarded:
            raise SonioxRealtimeError("This connection has already been discarded")
        if not self._ws:
            raise SonioxRealtimeError("Realtime STT connection is not open")
        if self._session_started:
            raise SonioxRealtimeError("This connection already has an active session")
        self.stop_idle_keepalive()
        key = api_key or self._api_key
        payload = config.build_payload(key)
        try:
            self._ws.send(json.dumps(payload.model_dump(exclude_none=True)))
        except Exception as exc:
            raise SonioxRealtimeError("Failed to start realtime STT session") from exc
        self._session_started = True
        return RealtimeSTTStream(self, payload)

    def _send_json(self, payload: dict[str, object]) -> None:
        if not self._ws:
            raise SonioxRealtimeError("Realtime STT connection is not open")
        try:
            self._ws.send(json.dumps(payload))
        except Exception as exc:
            raise SonioxRealtimeError("Failed to send STT control message") from exc

    def _send_bytes(self, chunk: bytes) -> None:
        if not self._ws:
            raise SonioxRealtimeError("Realtime STT connection is not open")
        try:
            self._ws.send(chunk)
        except Exception as exc:
            raise SonioxRealtimeError("Failed to send audio chunk") from exc

    def _send_empty(self) -> None:
        if not self._ws:
            raise SonioxRealtimeError("Realtime STT connection is not open")
        try:
            self._ws.send("")
        except Exception as exc:
            raise SonioxRealtimeError("Failed to send control message") from exc

    def _recv_bytes(self) -> bytes:
        if not self._ws:
            raise SonioxRealtimeError("Realtime STT connection is not open")
        try:
            message = self._ws.recv()
        except ConnectionClosed:
            self._ws = None
            return b""
        if isinstance(message, str):
            return message.encode("utf-8")
        return message


class RealtimeSTTStream:
    """
    An active realtime STT session on a :class:`RealtimeSTTConnection`.

    Created by :meth:`RealtimeSTTConnection.start_session` or
    :meth:`RealtimeSTTPreconnectPool.start_session`. Exposes the same
    streaming API as :class:`RealtimeSTTSession`.
    """

    def __init__(self, connection: RealtimeSTTConnection, config: RealtimeSTTConfig) -> None:
        self._connection = connection
        self._config = config
        self._last_message: RealtimeEvent | None = None
        self._paused = False
        self._keepalive: KeepaliveThread | None = None
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

    def send_byte_chunk(self, chunk: bytes) -> None:
        if self._paused:
            return
        self._connection._send_bytes(chunk)

    def send_bytes(self, chunks: bytes | Iterator[bytes], *, finish: bool = True) -> None:
        if isinstance(chunks, bytes):
            self.send_byte_chunk(chunks)
            return
        for chunk in chunks:
            self.send_byte_chunk(chunk)
        if finish:
            self.finish()

    def send_control_message(self, control_type: RealtimeControlType) -> None:
        if control_type == RealtimeControlType.FINISH:
            self._connection._send_empty()
        elif control_type == RealtimeControlType.KEEP_ALIVE:
            self._connection._send_json({"type": "keepalive"})
        elif control_type == RealtimeControlType.FINALIZE:
            self._connection._send_json({"type": "finalize"})

    def finish(self) -> None:
        self._finish_sent = True
        self.send_control_message(RealtimeControlType.FINISH)

    def keep_alive(self) -> None:
        self.send_control_message(RealtimeControlType.KEEP_ALIVE)

    def finalize(self) -> None:
        self.send_control_message(RealtimeControlType.FINALIZE)

    def recv_bytes(self) -> bytes:
        return self._connection._recv_bytes()

    def parse_event(self, raw: str | bytes) -> RealtimeEvent:
        return RealtimeEvent.validate_event(raw)

    def receive_event(self) -> RealtimeEvent | None:
        raw = self.recv_bytes()
        if not raw:
            return None
        event = self.parse_event(raw)
        self._last_message = event
        return event

    def receive_events(self) -> Iterator[RealtimeEvent]:
        while True:
            event = self.receive_event()
            if event is None:
                break
            yield event

    def handle_events(self, handler: Callable[[RealtimeEvent], None]) -> None:
        for event in self.receive_events():
            handler(event)

    def pause(self, *, finalize: bool = True) -> None:
        if self._paused:
            return
        if finalize:
            self.finalize()
        self._paused = True
        self._keepalive = KeepaliveThread(self.keep_alive, KEEP_ALIVE_INTERVAL_SEC)
        self._keepalive.start()

    def resume(self) -> None:
        if not self._paused:
            return
        if self._keepalive is not None:
            self._keepalive.stop()
            self._keepalive = None
        self._paused = False

    def close(self) -> None:
        """Discard the session link. It is never returned to a pool."""
        if self._keepalive is not None:
            self._keepalive.stop()
            self._keepalive = None
        self._paused = False
        self._connection.discard(send_finish=not self._finish_sent)


class RealtimeSTTPooledSession:
    """
    Realtime STT session backed by the client's internal connection pool.

    On enter, claims a pre-connected WebSocket from the pool and sends config.
    The public API matches :class:`RealtimeSTTSession`.
    """

    def __init__(
        self,
        pool: RealtimeSTTConnectionPool,
        config: RealtimeSTTConfig,
        *,
        api_key: str | None = None,
    ) -> None:
        self._pool = pool
        self._config = config
        self._api_key = api_key
        self._stream: RealtimeSTTStream | None = None

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

    def __enter__(self) -> RealtimeSTTPooledSession:
        self._pool.warmup()
        self._stream = self._pool.start_session(config=self._config, api_key=self._api_key)
        return self

    def __exit__(
        self,
        _exc_type: type[BaseException] | None,
        _exc_value: BaseException | None,
        _traceback: TracebackType | None,
    ) -> None:
        _ = (_exc_type, _exc_value, _traceback)
        self.close()

    def close(self) -> None:
        if self._stream is not None:
            self._stream.close()
            self._stream = None

    def _require_stream(self) -> RealtimeSTTStream:
        if self._stream is None:
            raise SonioxRealtimeError("Realtime session is not connected")
        return self._stream

    def send_byte_chunk(self, chunk: bytes) -> None:
        self._require_stream().send_byte_chunk(chunk)

    def send_bytes(self, chunks: bytes | Iterator[bytes], *, finish: bool = True) -> None:
        self._require_stream().send_bytes(chunks, finish=finish)

    def send_control_message(self, control_type: RealtimeControlType) -> None:
        self._require_stream().send_control_message(control_type)

    def finish(self) -> None:
        self._require_stream().finish()

    def keep_alive(self) -> None:
        self._require_stream().keep_alive()

    def finalize(self) -> None:
        self._require_stream().finalize()

    def recv_bytes(self) -> bytes:
        return self._require_stream().recv_bytes()

    def parse_event(self, raw: str | bytes) -> RealtimeEvent:
        return self._require_stream().parse_event(raw)

    def receive_event(self) -> RealtimeEvent | None:
        return self._require_stream().receive_event()

    def receive_events(self) -> Iterator[RealtimeEvent]:
        stream = self._require_stream()
        yield from stream.receive_events()

    def handle_events(self, handler: Callable[[RealtimeEvent], None]) -> None:
        self._require_stream().handle_events(handler)

    def pause(self, *, finalize: bool = True) -> None:
        self._require_stream().pause(finalize=finalize)

    def resume(self) -> None:
        self._require_stream().resume()

    enter = __enter__


@dataclass
class _PooledIdleLink:
    conn: RealtimeSTTConnection
    opened_at: float

    def age_sec(self) -> float:
        return time.monotonic() - self.opened_at

    def is_expired(self, max_lifetime_sec: float) -> bool:
        return self.age_sec() >= max_lifetime_sec

    def should_refresh(self, max_lifetime_sec: float, refresh_before_sec: float) -> bool:
        remaining = max_lifetime_sec - self.age_sec()
        return remaining <= refresh_before_sec


class RealtimeSTTConnectionPool:
    """
    Pool of idle WebSocket links to the realtime STT endpoint.

    Callers **borrow** a link with :meth:`borrow_connection`: the link is
    removed from the pool immediately. If the pool is empty at borrow time,
    a new WebSocket is opened synchronously. A background task then refills
    the pool up to ``pool_size``.

    Session links are discarded after use — they never return to the pool.
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
        self._idle: queue.Queue[_PooledIdleLink] = queue.Queue()
        self._closed = False
        self._replenish_lock = threading.Lock()
        self._maintenance: KeepaliveThread | None = None

    def __enter__(self) -> RealtimeSTTConnectionPool:
        self.warmup()
        return self

    def __exit__(
        self,
        _exc_type: type[BaseException] | None,
        _exc_value: BaseException | None,
        _traceback: TracebackType | None,
    ) -> None:
        _ = (_exc_type, _exc_value, _traceback)
        self.close()

    @property
    def idle_count(self) -> int:
        """Number of idle links currently available to borrow."""
        return self._idle.qsize()

    def borrow_connection(self) -> RealtimeSTTConnection:
        """
        Borrow an idle link from the pool.

        The link is **removed from the pool** before this returns. If no idle
        link is available, a new WebSocket is opened **immediately**
        (synchronous). The pool refills in the background afterward.

        The caller owns the returned link until
        :meth:`RealtimeSTTConnection.discard` (typically via
        :meth:`RealtimeSTTStream.close` after a session).
        """
        if self._closed:
            raise SonioxRealtimeError("Connection pool is closed")
        conn = self._borrow_connection()
        threading.Thread(target=self._replenish_one, daemon=True).start()
        return conn

    def warmup(self) -> None:
        """Open idle connections until the pool reaches ``pool_size``."""
        if self._closed:
            raise SonioxRealtimeError("Preconnect pool is closed")
        self._start_maintenance()
        while self._idle.qsize() < self._pool_size:
            self._idle.put(self._open_idle_link())

    def start_session(
        self,
        *,
        config: RealtimeSTTConfig,
        api_key: str | None = None,
    ) -> RealtimeSTTStream:
        """
        Borrow a link, send session config, and return a stream handle.

        Equivalent to :meth:`borrow_connection` followed by
        :meth:`RealtimeSTTConnection.start_session`.
        """
        conn = self.borrow_connection()
        try:
            return conn.start_session(config=config, api_key=api_key)
        except Exception:
            conn.discard()
            raise

    def close(self) -> None:
        """Close all idle connections and stop replenishing."""
        self._closed = True
        if self._maintenance is not None:
            self._maintenance.stop()
            self._maintenance = None
        while True:
            try:
                link = self._idle.get_nowait()
            except queue.Empty:
                break
            link.conn.close()

    def _start_maintenance(self) -> None:
        if self._maintenance is not None:
            return
        self._maintenance = KeepaliveThread(
            self._maintain_idle_links,
            self._keepalive_interval_sec,
        )
        self._maintenance.start()

    def _open_idle_link(self) -> _PooledIdleLink:
        conn = RealtimeSTTConnection(
            self._url,
            self._api_key,
            connect_timeout_sec=self._connect_timeout_sec,
        )
        conn.__enter__()
        if self._idle_keepalive:
            conn.start_idle_keepalive(interval_sec=self._keepalive_interval_sec)
        return _PooledIdleLink(conn=conn, opened_at=time.monotonic())

    def _borrow_connection(self) -> RealtimeSTTConnection:
        """Take one link out of the idle queue, or open a new one if empty."""
        while not self._closed:
            try:
                link = self._idle.get_nowait()
            except queue.Empty:
                return self._open_idle_link().conn
            if link.is_expired(self._idle_max_lifetime_sec):
                link.conn.close()
                continue
            if link.should_refresh(
                self._idle_max_lifetime_sec,
                self._idle_refresh_before_sec,
            ):
                link.conn.close()
                return self._open_idle_link().conn
            return link.conn
        raise SonioxRealtimeError("Connection pool is closed")

    def _maintain_idle_links(self) -> None:
        if self._closed:
            return
        with self._replenish_lock:
            if self._closed:
                return
            kept: list[_PooledIdleLink] = []
            while True:
                try:
                    link = self._idle.get_nowait()
                except queue.Empty:
                    break
                if link.is_expired(self._idle_max_lifetime_sec) or link.should_refresh(
                    self._idle_max_lifetime_sec,
                    self._idle_refresh_before_sec,
                ):
                    link.conn.close()
                else:
                    kept.append(link)
            for link in kept:
                self._idle.put(link)
            while self._idle.qsize() < self._pool_size:
                try:
                    self._idle.put(self._open_idle_link())
                except Exception:
                    break

    def _replenish_one(self) -> None:
        if self._closed:
            return
        with self._replenish_lock:
            if self._closed or self._idle.qsize() >= self._pool_size:
                return
            try:
                self._idle.put(self._open_idle_link())
            except Exception:
                return


RealtimeSTTPreconnectPool = RealtimeSTTConnectionPool
