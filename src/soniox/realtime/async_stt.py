from __future__ import annotations

import json
from collections.abc import AsyncIterator, Awaitable, Callable
from types import TracebackType
from typing import TYPE_CHECKING

from websockets import connect as async_ws_connect
from websockets.exceptions import ConnectionClosed

from ..errors import SonioxRealtimeError, SonioxValidationError
from ..types.realtime import RealtimeControlType, RealtimeEvent, RealtimeSttConfig

if TYPE_CHECKING:
    from ..client import AsyncSonioxClient


class AsyncRealtimeSTTSession:
    def __init__(self, url: str, config: RealtimeSttConfig) -> None:
        self._url = url
        self._config = config
        self._ws = None
        self._last_message: RealtimeEvent | None = None

    @property
    def config(self) -> RealtimeSttConfig:
        return self._config

    async def __aenter__(self) -> AsyncRealtimeSTTSession:
        try:
            self._ws = await async_ws_connect(self._url)
            await self._ws.send(json.dumps(self._config.model_dump(exclude_none=True)))
            return self
        except Exception as exc:
            if self._ws:
                try:
                    await self._ws.close()
                except Exception:
                    pass
                self._ws = None
            raise SonioxRealtimeError("Failed to start realtime session") from exc

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
            await self._ws.close()
        finally:
            self._ws = None

    async def send_byte_chunk(self, chunk: bytes) -> None:
        if not self._ws:
            raise SonioxRealtimeError("Realtime session is not connected")
        try:
            await self._ws.send(chunk)
        except Exception as exc:
            raise SonioxRealtimeError("Failed to send audio chunk") from exc

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
            raise SonioxRealtimeError("Failed to send control message") from exc

    async def send_finish(self) -> None:
        await self.send_control_message(RealtimeControlType.FINISH)

    async def send_keep_alive(self) -> None:
        await self.send_control_message(RealtimeControlType.KEEP_ALIVE)

    async def send_finalize(self) -> None:
        await self.send_control_message(RealtimeControlType.FINALIZE)

    async def recv_bytes(self) -> bytes:
        if not self._ws:
            raise SonioxRealtimeError("Realtime session is not connected")
        try:
            message = await self._ws.recv()
        except ConnectionClosed:
            return b""
        if isinstance(message, str):
            return message.encode("utf-8")
        return message

    def parse_event(self, raw: str | bytes) -> RealtimeEvent:
        return RealtimeEvent.validate_event(raw)

    @property
    def last_message(self) -> RealtimeEvent | None:
        return self._last_message

    async def receive_event(self) -> RealtimeEvent | None:
        if not self._ws:
            raise SonioxRealtimeError("Realtime session is not connected")
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

    async def handle_events(self, handler: Callable[[RealtimeEvent], Awaitable[None]]) -> None:
        async for event in self.receive_events():
            await handler(event)

    enter = __aenter__
    aenter = __aenter__


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
