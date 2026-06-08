from __future__ import annotations

from websockets import connect as async_ws_connect
from websockets.sync.client import connect as sync_ws_connect

__all__ = ["async_ws_connect", "sync_ws_connect"]
