from __future__ import annotations

import json
from collections.abc import AsyncIterator, Awaitable, Callable
from types import TracebackType
from typing import TYPE_CHECKING

from websockets import connect as async_ws_connect
from websockets.exceptions import ConnectionClosed

from ..errors import SonioxRealtimeError, SonioxValidationError
from ..types.realtime import (
    RealtimeControlType,
    RealtimeEvent,
    RealtimeSttConfig,
)
from .stt_base import BaseRealtimeSTTSession

if TYPE_CHECKING:
    from ..client import AsyncSonioxClient


class AsyncRealtimeSTTSession(BaseRealtimeSTTSession):
    async def __aenter__(self) -> AsyncRealtimeSTTSession:
        try:
            self._ws = await async_ws_connect(self._url)
            await self._ws.send(json.dumps(self._payload.model_dump(exclude_none=True)))
            self._emit_open()
            self._open_event_emitted = True
            return self
        except Exception:
            if self._ws:
                try:
                    await self._ws.close()
                except Exception:
                    pass
                self._ws = None
            raise

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
        except Exception:
            pass
        finally:
            try:
                await self._ws.close()
            except Exception:
                pass
            finally:
                self._ws = None
                self._emit_close()

    async def send_byte_chunk(self, chunk: bytes) -> None:
        if not self._ws:
            raise SonioxRealtimeError("Realtime session is not connected")
        try:
            await self._ws.send(chunk)
        except Exception as exc:
            self._emit_error(exc)
            raise

    async def send_bytes(self, chunks: bytes | AsyncIterator[bytes]) -> None:
        if isinstance(chunks, bytes):
            await self.send_byte_chunk(chunks)
            return

        async for chunk in chunks:
            await self.send_byte_chunk(chunk)
        await self.send_finish()

    async def send_control_message(self, control_type: RealtimeControlType) -> None:
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

    async def send_finish(self) -> None:
        await self.send_control_message(RealtimeControlType.FINISH)

    async def send_keep_alive(self) -> None:
        await self.send_control_message(RealtimeControlType.KEEP_ALIVE)

    async def send_finalize(self) -> None:
        await self.send_control_message(RealtimeControlType.FINALIZE)

    async def receive_event(self) -> RealtimeEvent | None:
        if not self._ws:
            raise SonioxRealtimeError("Realtime session is not connected")
        try:
            raw = await self._ws.recv()
        except ConnectionClosed:
            return None

        event = RealtimeEvent.validate_event(raw)
        self._handle_received_event(event)
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
