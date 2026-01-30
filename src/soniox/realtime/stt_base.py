from __future__ import annotations

import inspect
import logging
from collections.abc import Callable
from typing import Any

from ..errors import SonioxRealtimeError
from ..types.realtime import (
    RealtimeEvent,
    RealtimeSessionClosePayload,
    RealtimeSessionErrorPayload,
    RealtimeSessionEventPayload,
    RealtimeSessionFinishedPayload,
    RealtimeSessionMessagePayload,
    RealtimeSessionOpenPayload,
    RealtimeSttConfig,
)

logger = logging.getLogger(__name__)


class BaseRealtimeSTTSession:
    def __init__(self, url: str, payload: RealtimeSttConfig) -> None:
        self._url = url
        self._payload = payload
        self._ws = None
        self._listeners: dict[str, list[Callable[[Any], None]]] = {
            "open": [],
            "close": [],
            "message": [],
            "finished": [],
            "error": [],
        }
        self._open_event_emitted = False

    @property
    def client_reference_id(self) -> str | None:
        return self._payload.client_reference_id

    @property
    def is_connected(self) -> bool:
        return self._ws is not None

    def on_open(self, callback: Callable[[RealtimeSessionOpenPayload], None]) -> None:
        self._listeners["open"].append(callback)
        if self._open_event_emitted:
            payload = RealtimeSessionOpenPayload()
            self._safe_invoke_callback(callback, payload)

    def on_close(self, callback: Callable[[RealtimeSessionClosePayload], None]) -> None:
        self._listeners["close"].append(callback)

    def on_message(self, callback: Callable[[RealtimeSessionMessagePayload], None]) -> None:
        self._listeners["message"].append(callback)

    def on_finished(self, callback: Callable[[RealtimeSessionFinishedPayload], None]) -> None:
        self._listeners["finished"].append(callback)

    def on_error(self, callback: Callable[[RealtimeSessionErrorPayload], None]) -> None:
        self._listeners["error"].append(callback)

    def remove_listener(self, event_type: str, callback: Callable[[Any], None]) -> bool:
        try:
            self._listeners[event_type].remove(callback)
            return True
        except (KeyError, ValueError):
            return False

    def clear_listeners(self, event_type: str | None = None) -> None:
        if event_type:
            if event_type in self._listeners:
                self._listeners[event_type].clear()
        else:
            for listeners in self._listeners.values():
                listeners.clear()

    def _emit_open(self) -> None:
        payload = RealtimeSessionOpenPayload()
        self._emit("open", payload)

    def _emit_close(self) -> None:
        payload = RealtimeSessionClosePayload()
        self._emit("close", payload)

    def _emit_message(self, event: RealtimeEvent) -> None:
        payload = RealtimeSessionMessagePayload(event=event)
        self._emit("message", payload)

    def _emit_finished(self, event: RealtimeEvent) -> None:
        payload = RealtimeSessionFinishedPayload(event=event)
        self._emit("finished", payload)

    def _emit_error(self, error: Exception) -> None:
        payload = RealtimeSessionErrorPayload(error=error)
        self._emit("error", payload)

    def _emit(self, event_type: str, payload: RealtimeSessionEventPayload) -> None:
        for callback in self._listeners[event_type]:
            self._safe_invoke_callback(callback, payload)

    def _safe_invoke_callback(
        self, callback: Callable[[Any], None], payload: RealtimeSessionEventPayload
    ) -> None:
        try:
            self._invoke_callback(callback, payload)
        except Exception as exc:
            logger.error(
                f"Error in callback for {payload.type} event: {exc}",
                exc_info=True,
            )

    def _invoke_callback(
        self, callback: Callable[[Any], None], payload: RealtimeSessionEventPayload
    ) -> None:
        parameters = [
            p
            for p in inspect.signature(callback).parameters.values()
            if p.kind in (inspect.Parameter.POSITIONAL_ONLY, inspect.Parameter.POSITIONAL_OR_KEYWORD)
        ]
        if len(parameters) >= 2:
            callback(payload, self)
        else:
            callback(payload)

    def _handle_received_event(self, event: RealtimeEvent) -> None:
        self._emit_message(event)

        if event.finished:
            self._emit_finished(event)

        if event.error_code:
            error = SonioxRealtimeError(
                f"Realtime error {event.error_code}: {event.error_message or 'unknown'}"
            )
            self._emit_error(error)
            if not self._listeners["error"]:
                raise error
