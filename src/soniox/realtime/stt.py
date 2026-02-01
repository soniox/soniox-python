from __future__ import annotations

import json
from collections.abc import Callable, Iterator
from types import TracebackType
from typing import TYPE_CHECKING

from websockets.exceptions import ConnectionClosed
from websockets.sync.client import connect as sync_ws_connect

from ..errors import SonioxRealtimeError, SonioxValidationError
from ..types.realtime import RealtimeControlType, RealtimeEvent, RealtimeSttConfig

if TYPE_CHECKING:
    from ..client import SonioxClient


class RealtimeSTTSession:
    def __init__(self, url: str, config: RealtimeSttConfig) -> None:
        self._url = url
        self._config = config
        self._ws = None

    @property
    def config(self) -> RealtimeSttConfig:
        return self._config

    def __enter__(self) -> RealtimeSTTSession:
        try:
            self._ws = sync_ws_connect(self._url)
            self._ws.send(json.dumps(self._config.model_dump(exclude_none=True)))
            return self
        except Exception as exc:
            # Cleanup on failure
            if self._ws:
                try:
                    self._ws.close()
                except Exception:
                    pass
                self._ws = None
            raise SonioxRealtimeError("Failed to start realtime session") from exc

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
            self._ws.close()
        finally:
            self._ws = None

    def send_byte_chunk(self, chunk: bytes) -> None:
        if not self._ws:
            raise SonioxRealtimeError("Realtime session is not connected")
        try:
            self._ws.send(chunk)
        except Exception as exc:
            raise SonioxRealtimeError("Failed to send audio chunk") from exc

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
            raise SonioxRealtimeError("Failed to send control message") from exc

    def send_finish(self) -> None:
        self.send_control_message(RealtimeControlType.FINISH)

    def send_keep_alive(self) -> None:
        self.send_control_message(RealtimeControlType.KEEP_ALIVE)

    def send_finalize(self) -> None:
        self.send_control_message(RealtimeControlType.FINALIZE)

    def recv_bytes(self) -> bytes:
        if not self._ws:
            raise SonioxRealtimeError("Realtime session is not connected")
        try:
            message = self._ws.recv()
        except ConnectionClosed:
            return b""
        if isinstance(message, str):
            return message.encode("utf-8")
        return message

    def parse_event(self, raw: str | bytes) -> RealtimeEvent:
        return RealtimeEvent.validate_event(raw)

    def receive_event(self) -> RealtimeEvent | None:
        if not self._ws:
            raise SonioxRealtimeError("Realtime session is not connected")
        raw = self.recv_bytes()
        if not raw:
            return None
        return self.parse_event(raw)

    def receive_events(self) -> Iterator[RealtimeEvent]:
        while True:
            event = self.receive_event()
            if event is None:
                break
            yield event

    def handle_events(self, handler: Callable[[RealtimeEvent], None]) -> None:
        for event in self.receive_events():
            handler(event)

    enter = __enter__


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
