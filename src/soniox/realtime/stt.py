from __future__ import annotations

import json
from collections.abc import Callable, Iterator
from types import TracebackType
from typing import TYPE_CHECKING, Annotated, Literal, TypeVar

from pydantic import BaseModel, ConfigDict, Field
from websockets.exceptions import ConnectionClosed
from websockets.sync.client import connect as sync_ws_connect

from ..errors import SonioxRealtimeError, SonioxValidationError
from ..types.realtime import (
    RealtimeControlType,
    RealtimeEvent,
    RealtimeSessionEvent,
    RealtimeSttConfig,
)


class RealtimeSessionPayload(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    session: RealtimeSTTSession


class RealtimeSessionOpenPayload(RealtimeSessionPayload):
    type: Literal["open"] = "open"


class RealtimeSessionClosePayload(RealtimeSessionPayload):
    type: Literal["close"] = "close"


class RealtimeSessionMessagePayload(RealtimeSessionPayload):
    type: Literal["message"] = "message"
    event: RealtimeEvent


class RealtimeSessionFinishedPayload(RealtimeSessionPayload):
    type: Literal["finished"] = "finished"
    event: RealtimeEvent


class RealtimeSessionErrorPayload(RealtimeSessionPayload):
    type: Literal["error"] = "error"
    error: Exception


RealtimeSessionEventPayload = Annotated[
    RealtimeSessionOpenPayload
    | RealtimeSessionClosePayload
    | RealtimeSessionMessagePayload
    | RealtimeSessionFinishedPayload
    | RealtimeSessionErrorPayload,
    Field(discriminator="type"),
]


RealtimePayloadCallback = Callable[[RealtimeSessionEventPayload], None]
RealtimeSessionCallback = Callable[[RealtimeSessionEvent, "RealtimeSTTSession"], None]
RealtimeErrorCallback = Callable[[Exception, "RealtimeSTTSession"], None]

if TYPE_CHECKING:
    from ..client import SonioxClient


PayloadT = TypeVar("PayloadT", bound=RealtimeSessionEventPayload)


class RealtimeSTTSession:
    def __init__(self, url: str, payload: RealtimeSttConfig) -> None:
        self._url = url
        self._payload = payload
        self._ws = None
        self._listeners: dict[RealtimeSessionEvent, list[RealtimePayloadCallback]] = {}
        self._open_event_emitted = False

        # context manager

    def __enter__(self) -> RealtimeSTTSession:
        self._ws = sync_ws_connect(self._url)
        self._ws.send(json.dumps(self._payload.model_dump(exclude_none=True)))
        self._emit(RealtimeSessionEvent.OPEN)
        self._open_event_emitted = True
        return self

    def __exit__(
        self,
        _exc_type: type[BaseException] | None,
        _exc_value: BaseException | None,
        _traceback: TracebackType | None,
    ) -> None:
        _ = (_exc_type, _exc_value, _traceback)  # To make linter happy.
        self.close()

        # session methods

    def close(self) -> None:
        if not self._ws:
            return
        try:
            self._ws.send("")
        except ConnectionClosed:
            pass
        finally:
            self._ws.close()
            self._ws = None
        self._emit(RealtimeSessionEvent.CLOSE)

    # session methods what we send to soniox

    def send_byte_chunk(self, chunk: bytes) -> None:
        if not self._ws:
            raise SonioxRealtimeError("Realtime session is not connected")
        try:
            self._ws.send(chunk)
        except Exception as exc:
            self._emit_error(exc)
            raise

    def send_bytes(
        self,
        chunks: bytes | Iterator[bytes],
    ) -> None:
        if isinstance(chunks, bytes):
            self.send_byte_chunk(bytes(chunks))
            return

        for chunk in chunks:
            self.send_byte_chunk(bytes(chunk))
        self.send_finish()

    def send_control_message(
        self,
        control_type: RealtimeControlType,
    ) -> None:
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

        # session events (what soniox sends us)

    def receive_event(self) -> RealtimeEvent | None:
        if not self._ws:
            raise SonioxRealtimeError("Realtime session is not connected")
        try:
            raw = self._ws.recv()
        except ConnectionClosed:
            return None
        event = RealtimeEvent.validate_event(raw)
        self._emit(RealtimeSessionEvent.MESSAGE, event)
        if event.finished:
            self._emit(RealtimeSessionEvent.FINISHED, event)
        if event.error_code:
            error = SonioxRealtimeError(
                f"Realtime error {event.error_code}: {event.error_message or 'unknown'}"
            )
            self._emit(RealtimeSessionEvent.ERROR, error)
            if not self._listeners.get(RealtimeSessionEvent.ERROR):
                raise error
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

    # callbacks

    def on_event(
        self,
        event_type: RealtimeSessionEvent,
        callback: RealtimePayloadCallback,
    ) -> None:
        self._listeners.setdefault(event_type, []).append(callback)

    def on_message(self, callback: Callable[[RealtimeSessionMessagePayload], None]) -> None:
        self._register_callback(
            RealtimeSessionEvent.MESSAGE, RealtimeSessionMessagePayload, callback
        )

    def on_open(self, callback: Callable[[RealtimeSessionOpenPayload], None]) -> None:
        self._register_callback(RealtimeSessionEvent.OPEN, RealtimeSessionOpenPayload, callback)
        if self._open_event_emitted:
            callback(RealtimeSessionOpenPayload(session=self))

    def on_close(self, callback: Callable[[RealtimeSessionClosePayload], None]) -> None:
        self._register_callback(RealtimeSessionEvent.CLOSE, RealtimeSessionClosePayload, callback)

    def on_error(self, callback: Callable[[RealtimeSessionErrorPayload], None]) -> None:
        self._register_callback(RealtimeSessionEvent.ERROR, RealtimeSessionErrorPayload, callback)

    def on_finished(self, callback: Callable[[RealtimeSessionFinishedPayload], None]) -> None:
        self._register_callback(
            RealtimeSessionEvent.FINISHED, RealtimeSessionFinishedPayload, callback
        )

    def _register_callback(
        self,
        event_type: RealtimeSessionEvent,
        payload_type: type[PayloadT],
        callback: Callable[[PayloadT], None],
    ) -> None:
        def _wrapper(payload: RealtimeSessionEventPayload) -> None:
            if isinstance(payload, payload_type):
                callback(payload)

        self._listeners.setdefault(event_type, []).append(_wrapper)

    @property
    def client_reference_id(self) -> str | None:
        return self._payload.client_reference_id

    def _emit(
        self, event_type: RealtimeSessionEvent, payload: RealtimeEvent | Exception | None = None
    ) -> None:
        event_payload = self._build_event_payload(event_type, payload)
        for callback in self._listeners.get(event_type, []):
            try:
                callback(event_payload)
            except Exception:
                pass

    def _build_event_payload(
        self,
        event_type: RealtimeSessionEvent,
        payload: RealtimeEvent | Exception | None = None,
    ) -> RealtimeSessionEventPayload:
        if event_type is RealtimeSessionEvent.MESSAGE and isinstance(payload, RealtimeEvent):
            return RealtimeSessionMessagePayload(session=self, event=payload)
        if event_type is RealtimeSessionEvent.FINISHED and isinstance(payload, RealtimeEvent):
            return RealtimeSessionFinishedPayload(session=self, event=payload)
        if event_type is RealtimeSessionEvent.ERROR and isinstance(payload, Exception):
            return RealtimeSessionErrorPayload(session=self, error=payload)
        if event_type is RealtimeSessionEvent.OPEN:
            return RealtimeSessionOpenPayload(session=self)
        return RealtimeSessionClosePayload(session=self)

    def _emit_error(self, exc: Exception) -> None:
        self._emit(RealtimeSessionEvent.ERROR, exc)


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
