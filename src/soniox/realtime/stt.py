from __future__ import annotations

import json
from collections.abc import Callable, Iterator
from types import TracebackType
from typing import TYPE_CHECKING, Literal, TypeVar

from websockets.exceptions import ConnectionClosed
from websockets.sync.client import connect as sync_ws_connect

from ..errors import SonioxRealtimeError, SonioxValidationError
from ..types.realtime import (
    RealtimeControlType,
    RealtimeEvent,
    RealtimeSessionClosePayload,
    RealtimeSessionErrorPayload,
    RealtimeSessionEventPayload,
    RealtimeSessionFinishedPayload,
    RealtimeSessionOpenPayload,
    RealtimeSttConfig,
)

if TYPE_CHECKING:
    from ..client import SonioxClient

ListenerType = Literal["open", "close", "finished", "error"]
PayloadT = TypeVar("PayloadT", bound=RealtimeSessionEventPayload)

OpenCallback = Callable[[RealtimeSessionOpenPayload, "RealtimeSTTSession"], None]
CloseCallback = Callable[[RealtimeSessionClosePayload, "RealtimeSTTSession"], None]
FinishedCallback = Callable[[RealtimeSessionFinishedPayload, "RealtimeSTTSession"], None]
ErrorCallback = Callable[[RealtimeSessionErrorPayload, "RealtimeSTTSession"], None]


class RealtimeSTTSession:
    def __init__(self, url: str, config: RealtimeSttConfig) -> None:
        self._url = url
        self._config = config
        self._ws = None
        self._open_callbacks: list[OpenCallback] = []
        self._close_callbacks: list[CloseCallback] = []
        self._finished_callbacks: list[FinishedCallback] = []
        self._error_callbacks: list[ErrorCallback] = []
        self._open_event_emitted = False

    @property
    def config(self) -> RealtimeSttConfig:
        return self._config

    def on_open(self, callback: OpenCallback) -> None:
        self._open_callbacks.append(callback)
        if self._open_event_emitted:
            self._emit_open()

    def on_close(self, callback: CloseCallback) -> None:
        self._close_callbacks.append(callback)

    def on_finished(self, callback: FinishedCallback) -> None:
        self._finished_callbacks.append(callback)

    def on_error(self, callback: ErrorCallback) -> None:
        self._error_callbacks.append(callback)

    def _emit_open(self) -> None:
        payload = RealtimeSessionOpenPayload()
        for callback in self._open_callbacks:
            callback(payload, self)

    def _emit_close(self) -> None:
        payload = RealtimeSessionClosePayload()
        for callback in self._close_callbacks:
            callback(payload, self)

    def _emit_finished(self, event: RealtimeEvent) -> None:
        payload = RealtimeSessionFinishedPayload(event=event)
        for callback in self._finished_callbacks:
            callback(payload, self)

    def _emit_error(self, error: Exception, event: RealtimeEvent | None = None) -> None:
        payload = RealtimeSessionErrorPayload(error=error, event=event)
        for callback in self._error_callbacks:
            callback(payload, self)

    def _handle_received_event(self, event: RealtimeEvent) -> None:
        if event.finished:
            self._emit_finished(event)

        if event.error_code:
            error = SonioxRealtimeError(
                f"Realtime error {event.error_code}: {event.error_message or 'unknown'}"
            )
            self._emit_error(error, event)
            if not self._error_callbacks:
                raise error

    def __enter__(self) -> RealtimeSTTSession:
        try:
            self._ws = sync_ws_connect(self._url)
            self._ws.send(json.dumps(self._config.model_dump(exclude_none=True)))
            self._emit_open()
            self._open_event_emitted = True
            return self
        except Exception:
            # Cleanup on failure
            if self._ws:
                try:
                    self._ws.close()
                except Exception:
                    pass
                self._ws = None
            raise

    def __exit__(
        self,
        _exc_type: type[BaseException] | None,
        _exc_value: BaseException | None,
        _traceback: TracebackType | None,
    ) -> None:
        _ = (_exc_type, _exc_value, _traceback)  # To make linter happy.
        self.close()

    def close(self) -> None:
        if not self._ws:
            return
        try:
            self._ws.send("")
        except ConnectionClosed:
            pass
        except Exception:
            pass
        finally:
            try:
                self._ws.close()
            except Exception:
                pass
            finally:
                self._ws = None
                self._emit_close()

    def send_byte_chunk(self, chunk: bytes) -> None:
        if not self._ws:
            raise SonioxRealtimeError("Realtime session is not connected")
        try:
            self._ws.send(chunk)
        except Exception as exc:
            self._emit_error(exc)
            raise

    def send_bytes(self, chunks: bytes | Iterator[bytes]) -> None:
        if isinstance(chunks, bytes):
            self.send_byte_chunk(chunks)
            return

        for chunk in chunks:
            self.send_byte_chunk(chunk)
        self.send_finish()

    def send_control_message(self, control_type: RealtimeControlType) -> None:
        if not self._ws:
            raise SonioxRealtimeError("Realtime session is not connected")
        try:
            if control_type == RealtimeControlType.FINISH:
                self._ws.send("")
            elif control_type == RealtimeControlType.KEEP_ALIVE:
                self._ws.send(json.dumps({"type": "keepalive"}))
            elif control_type == RealtimeControlType.FINALIZE:
                self._ws.send(json.dumps({"type": "finalize"}))
        except Exception as exc:
            self._emit_error(exc)
            raise

    def send_finish(self) -> None:
        self.send_control_message(RealtimeControlType.FINISH)

    def send_keep_alive(self) -> None:
        self.send_control_message(RealtimeControlType.KEEP_ALIVE)

    def send_finalize(self) -> None:
        self.send_control_message(RealtimeControlType.FINALIZE)

    def receive_event(self) -> RealtimeEvent | None:
        if not self._ws:
            raise SonioxRealtimeError("Realtime session is not connected")
        try:
            raw = self._ws.recv()
        except ConnectionClosed:
            return None

        event = RealtimeEvent.validate_event(raw)
        self._handle_received_event(event)
        return event

    def receive_events(self) -> Iterator[RealtimeEvent]:
        while True:
            event = self.receive_event()
            if event is None:
                break
            yield event
            if event.finished or event.error_code:
                break

    def handle_events(self, handler: Callable[[RealtimeEvent], None]) -> None:
        for event in self.receive_events():
            handler(event)


class RealtimeSTTClient:
    def __init__(self, client: SonioxClient) -> None:
        self._client = client

    def connect(
        self,
        *,
        config: RealtimeSttConfig,
        api_key: str | None = None,
    ) -> RealtimeSTTSession:
        key = api_key or self._client.api_key
        if not key:
            raise SonioxValidationError("API key is required to start a realtime session")

        payload = config.build_payload(key)
        return RealtimeSTTSession(
            self._client.websocket_base_url,
            payload,
        )
