"""
Property-style fuzz test for the realtime STT session.

Invariant under test: whatever random sequence of server events, connection
drops, and client send operations we throw at a session, the only exception
type allowed to escape is :class:`SonioxRealtimeError`. Anything else -
``AttributeError`` or ``KeyError`` from un-validated data, a bare
``ConnectionClosed`` leaking past the session's translation layer - is a bug.

The test is deterministic: one seed per parametrize iteration.
"""

from __future__ import annotations

import random
from unittest.mock import patch

import pytest
from websockets.exceptions import ConnectionClosed

from soniox.client import SonioxClient
from soniox.errors import SonioxRealtimeError
from soniox.types.realtime import RealtimeSTTConfig

from .mock_ws import MockWebSocket

CONFIG = RealtimeSTTConfig(model="v1")

# The only exception type documented to escape the public session API.
ALLOWED_ESCAPES = (SonioxRealtimeError,)


def _random_event(rng: random.Random) -> dict:
    """Build a plausibly-shaped server event."""
    tokens = [
        {"text": rng.choice(["hi", "world", ""]), "is_final": rng.random() < 0.3}
        for _ in range(rng.randint(0, 3))
    ]
    event: dict = {"tokens": tokens}
    roll = rng.random()
    if roll < 0.05:
        event["error_code"] = rng.choice([400, 429, 500])
        event["error_message"] = "fuzz"
    elif roll < 0.15:
        event["finished"] = True
    return event


def _script_session(rng: random.Random, ws: MockWebSocket) -> list[str]:
    """Queue a random server script and return the client-side action plan."""
    for _ in range(rng.randint(0, 8)):
        ws.push_recv(_random_event(rng))
    if rng.random() < 0.4:
        ws.push_recv_error(ConnectionClosed(None, None))
    else:
        ws.close_after_recv()

    actions = [
        rng.choice(["audio", "keepalive", "finalize"]) for _ in range(rng.randint(0, 5))
    ]
    if rng.random() < 0.8:
        actions.append("finish")
    return actions


def _drive(session, actions: list[str]) -> None:
    """Execute the planned actions, stopping at the first allowed escape."""
    for action in actions:
        try:
            if action == "audio":
                session.send_byte_chunk(b"chunk")
            elif action == "keepalive":
                session.keep_alive()
            elif action == "finalize":
                session.finalize()
            elif action == "finish":
                session.finish()
        except ALLOWED_ESCAPES:
            return
    try:
        for _ in session.receive_events():
            pass
    except ALLOWED_ESCAPES:
        pass


@pytest.mark.parametrize("seed", range(25))
def test_realtime_session_survives_random_failures(client: SonioxClient, seed: int) -> None:
    rng = random.Random(seed)
    ws = MockWebSocket()
    actions = _script_session(rng, ws)

    with patch("soniox.realtime.stt.sync_ws_connect", return_value=ws):
        try:
            with client.realtime.stt.connect(config=CONFIG) as session:
                _drive(session, actions)
        except ALLOWED_ESCAPES:
            pass
