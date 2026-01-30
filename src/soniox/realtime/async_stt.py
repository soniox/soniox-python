from __future__ import annotations

import json
from collections.abc import AsyncIterator, Awaitable, Callable
from types import TracebackType
from typing import TYPE_CHECKING, Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field
from websockets import ClientConnection
from websockets import connect as async_ws_connect
from websockets.exceptions import ConnectionClosed

from ..errors import SonioxRealtimeError, SonioxValidationError
from ..types.realtime import (
    RealtimeControlType,
    RealtimeEvent,
    RealtimeSessionEvent,
    RealtimeSttConfig,
)


class RealtimeSessionPayload(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    session: AsyncRealtimeSTTSession


class RealtimeSessionOpenPayload(RealtimeSessionPayload):
    type: Literal["open"] = "open"


class RealtimeSessionClosePayload(RealtimeSessionPayload):
    type: Literal["close"] = "close"


class RealtimeSessionMessagePayload(RealtimeSessionPayload):
    type: Literal["message"] = "message"
    event: RealtimeEvent


class RealtimeSessionErrorPayload(RealtimeSessionPayload):
    type: Literal["error"] = "error"
    error: Exception


RealtimeSessionEventPayload = Annotated[
    RealtimeSessionOpenPayload
    | RealtimeSessionClosePayload
    | RealtimeSessionMessagePayload
    | RealtimeSessionErrorPayload,
    Field(discriminator="type"),
]


RealtimePayloadCallback = Callable[[RealtimeSessionEventPayload], None]
RealtimeSessionCallback = Callable[[RealtimeSessionEvent, "AsyncRealtimeSTTSession"], None]
RealtimeErrorCallback = Callable[[Exception, "AsyncRealtimeSTTSession"], None]

if TYPE_CHECKING:
    from ..client import AsyncSonioxClient


class AsyncRealtimeSTTSession:
    def __init__(self, url: str, payload: RealtimeSttConfig) -> None:
        self._url: str = url
        self._payload: RealtimeSttConfig = payload
        self._ws: ClientConnection | None = None
        self._listeners: dict[RealtimeSessionEvent, list[RealtimePayloadCallback]] = {}
        self._open_event_emitted: bool = False

    async def __aenter__(self) -> AsyncRealtimeSTTSession:
        self._ws = await async_ws_connect(self._url)
        await self._ws.send(json.dumps(self._payload.model_dump(exclude_none=True)))
        self._emit(RealtimeSessionEvent.OPEN)
        self._open_event_emitted = True
        return self

    async def __aexit__(
        self,
        _exc_type: type[BaseException] | None,
        _exc_value: BaseException | None,
        _traceback: TracebackType | None,
    ) -> None:
        _ = (_exc_type, _exc_value, _traceback)  # To make linter happy.
        await self.close()

    async def close(self) -> None:
        if not self._ws:
            return
        try:
            await self._ws.send("")
        except ConnectionClosed:
            pass
        finally:
            await self._ws.close()
            self._ws = None
        self._emit(RealtimeSessionEvent.CLOSE)

    async def send_byte_chunk(self, chunk: bytes) -> None:
        if not self._ws:
            raise SonioxRealtimeError("Realtime session is not connected")
        try:
            await self._ws.send(chunk)
        except Exception as exc:
            self._emit_error(exc)
            raise

    async def send_bytes(
        self,
        chunks: bytes | AsyncIterator[bytes],
    ) -> None:
        if isinstance(chunks, bytes):
            await self.send_byte_chunk(bytes(chunks))
            return

        async for chunk in chunks:
            await self.send_byte_chunk(bytes(chunk))
        await self.send_finish()

    async def send_control_message(
        self,
        control_type: RealtimeControlType,
    ) -> None:
        if not self._ws:
            raise SonioxRealtimeError("Realtime session is not connected")
        try:
            if control_type == RealtimeControlType.FINISH:
                await self._ws.send("")
            elif control_type == RealtimeControlType.KEEP_ALIVE:
                await self._ws.send(json.dumps({"type": "keepalive"}))
            elif control_type == RealtimeControlType.FINALIZE:
                await self._ws.send(json.dumps({"type": "finalize"}))
        except Exception as exc:
            self._emit_error(exc)
            raise

    async def receive_event(self) -> RealtimeEvent | None:
        if not self._ws:
            raise SonioxRealtimeError("Realtime session is not connected")
        try:
            raw = await self._ws.recv()
        except ConnectionClosed:
            return None
        event = RealtimeEvent.validate_event(raw)
        self._emit(RealtimeSessionEvent.MESSAGE, event)
        if event.error_code:
            error = SonioxRealtimeError(
                f"Realtime error {event.error_code}: {event.error_message or 'unknown'}"
            )
            self._emit(RealtimeSessionEvent.ERROR, error)
            if not self._listeners.get(RealtimeSessionEvent.ERROR):
                raise error
        return event

    async def receive_events(self) -> AsyncIterator[RealtimeEvent]:
        while True:
            event = await self.receive_event()
            if event is None:
                break
            yield event
            if event.finished or event.error_code:
                break

    async def handle_events(self, handler: Callable[[RealtimeEvent], Awaitable[None]]) -> None:
        async for event in self.receive_events():
            await handler(event)

    def on_event(
        self,
        event_type: RealtimeSessionEvent,
        callback: RealtimePayloadCallback,
    ) -> None:
        self._listeners.setdefault(event_type, []).append(callback)

    def on_message(self, callback: Callable[[RealtimeSessionMessagePayload], None]) -> None:
        def _wrapper(payload: RealtimeSessionEventPayload) -> None:
            if payload.type == "message":
                callback(payload)

        self.on_event(RealtimeSessionEvent.MESSAGE, _wrapper)

    def on_open(self, callback: Callable[[RealtimeSessionOpenPayload], None]) -> None:
        def _wrapper(payload: RealtimeSessionEventPayload) -> None:
            if payload.type == "open":
                callback(payload)

        self.on_event(RealtimeSessionEvent.OPEN, _wrapper)
        if self._open_event_emitted:
            callback(RealtimeSessionOpenPayload(session=self))

    def on_close(self, callback: Callable[[RealtimeSessionClosePayload], None]) -> None:
        def _wrapper(payload: RealtimeSessionEventPayload) -> None:
            if payload.type == "close":
                callback(payload)

        self.on_event(RealtimeSessionEvent.CLOSE, _wrapper)

    def on_error(self, callback: Callable[[RealtimeSessionErrorPayload], None]) -> None:
        def _wrapper(payload: RealtimeSessionEventPayload) -> None:
            if payload.type == "error":
                callback(payload)

        self.on_event(RealtimeSessionEvent.ERROR, _wrapper)

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
        if event_type is RealtimeSessionEvent.ERROR and isinstance(payload, Exception):
            return RealtimeSessionErrorPayload(session=self, error=payload)
        if event_type is RealtimeSessionEvent.OPEN:
            return RealtimeSessionOpenPayload(session=self)
        return RealtimeSessionClosePayload(session=self)

    def _emit_error(self, exc: Exception) -> None:
        self._emit(RealtimeSessionEvent.ERROR, exc)

    @property
    def client_reference_id(self) -> str | None:
        return self._payload.client_reference_id

    async def send_finish(self) -> None:
        await self.send_control_message(RealtimeControlType.FINISH)

    async def send_keep_alive(self) -> None:
        await self.send_control_message(RealtimeControlType.KEEP_ALIVE)

    async def send_finalize(self) -> None:
        await self.send_control_message(RealtimeControlType.FINALIZE)


class AsyncRealtimeSTTClient:
    def __init__(self, client: AsyncSonioxClient) -> None:
        self._client = client

    def connect(
        self,
        *,
        config: RealtimeSttConfig,
        api_key: str | None = None,
    ) -> AsyncRealtimeSTTSession:
        key = api_key or self._client.api_key
        if not key:
            raise SonioxValidationError("API key is required to start a realtime session")

        payload = config.build_payload(key)
        return AsyncRealtimeSTTSession(
            self._client.websocket_base_url,
            payload,
        )
