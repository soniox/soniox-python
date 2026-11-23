"""
The stream reconnect protocol: what a dropped stream needs to come back.

A realtime STT stream that loses its connection carries on on a new one. The
server names the terms - how long a stream waits to be continued, which
messages it counts - and this module holds our side of them: the constants taken from the protocol, the state a stream is in once it
is no longer simply live, and the bookkeeping that says what to send again.

No I/O and no locking here. The session owns the socket and serializes the
calls; this only remembers.
"""

from __future__ import annotations

import json
import time
from collections import deque
from enum import Enum

PING_INTERVAL_SEC: float = 2.0
"""How often to ping, and how late a pong may be before the connection is lost.

A ceiling on both, which `min(idle_timeout / 4, …)` can lower. The docs ask for
a quarter of the idle timeout - 5s at the default - and 2s is deliberately
tighter: noticing a drop takes at most 4s rather than 10s, leaving most of the
reconnect window to get back in. The cost is a takeover where the docs' pace
would have ridden the delay out, which costs a connection, not the stream.
"""

CLOSE_DIAL_TIMEOUT_SEC: float = 1.0
"""How long closing may spend taking a stream over just to end it.

A session closed while it was taking the stream over has no socket to end the
stream on, and a stream nobody ends waits out its idle timeout. Bounded tight,
because this is on the caller's way out.
"""

MAX_RESUMES_WITHOUT_A_FRAME: int = 5
"""How many times a stream may be continued with nothing coming back.

A connection that answers and then dies before the resend reaches it leaves
this session with a new token and a fresh window, so nothing in the protocol
would ever stop it trying again. So this one is ours: a stream
continued over and over with no response in between is not coming back.

Each turn of that loop costs a connection and a round trip, and a stream that
is working answers something - a result, or a pong every couple of seconds -
between one drop and the next. Five consecutive silent takeovers is already far
past any real run of drops, and stops a runaway in well under a second.
"""

RECONNECT_REPLY_TIMEOUT_SEC: float = 5.0
"""How long to wait for an answer to the reconnect message.

A quarter of the window, at the default idle timeout, which is the pace the
documentation asks of an attempt.
"""


class Ending(Enum):
    """How far a session is from over, once it is no longer simply live.

    Named for the stream rather than for whoever acted, because that is what
    every reader of it wants to know. `CLOSING` is the only one with a stream
    still out there: the caller is done, but nothing has told the server yet.
    No ending at all is the only state that may take a dropped stream over.
    """

    CLOSING = "the caller is done, and the stream has not been told"
    ENDED = "the stream is over"
    TAKEN = "a newer connection has the stream"


class Reconnect:
    """
    What a stream has to remember to continue on a new connection.

    Bookkeeping only, no I/O and no locking: the session owns the socket and
    serializes the calls. The server counts the messages it received, so every
    message that counts - audio, keepalive, finalize, agent text, end of audio -
    goes through `record`, and none of the others do.

    A pong says the server received everything sent before its ping, so that is
    when messages are dropped from the resend log. Pinging is what keeps the log
    small; without it, it would have to hold every message of the reconnect
    window.
    """

    def __init__(self) -> None:
        self.token: str | None = None
        self.url: str | None = None
        self.last_seq: int = 0
        self.acked_at: float = time.monotonic()
        """
        When the server last proved it had our messages.

        The stream's reconnect window runs from the last message the server
        received, and on a silent drop that is before we noticed, so this is
        where the window is counted from rather than from the drop.
        """
        self.stream_started: bool = False
        """
        Whether anything has arrived from the server on this stream yet.

        A ping sent right after the start request is answered only once the
        stream starts, so until then an unanswered ping says nothing about the
        connection - and counting it kills streams that are slow to open.
        """
        self.resumes_without_a_frame: int = 0
        """
        Takeovers since the server last sent anything on this stream.

        A connection can answer `reconnected` and die before the resend
        reaches it, and every success rotates the token and starts the window
        again - so without this the stream is continued again and again, as
        fast as connections can be opened, with nothing to stop it.
        """
        self._count: int = 0
        self._unconfirmed: deque[tuple[int, str | bytes]] = deque()
        self._pings: dict[int, tuple[int, float]] = {}
        self._next_ping_id: int = 1

    def record(self, message: str | bytes) -> None:
        """Keep a message that counts, before it goes out."""
        self._count += 1
        self._unconfirmed.append((self._count, message))

    def ping(self) -> str:
        """The next ping, which the server answers with a pong carrying its id."""
        ping_id = self._next_ping_id
        self._next_ping_id += 1
        self._pings[ping_id] = (self._count, time.monotonic())
        return json.dumps({"type": "ping", "id": ping_id})

    def pong(self, ping_id: int | None) -> None:
        """Drop the messages the server had already received when it sent this pong."""
        sent = self._pings.pop(ping_id, None) if ping_id is not None else None
        if sent is None:
            return
        self.acked_at = time.monotonic()
        confirmed = sent[0]
        while self._unconfirmed and self._unconfirmed[0][0] <= confirmed:
            self._unconfirmed.popleft()

    def pong_overdue(self, timeout_sec: float) -> bool:
        """Whether a ping has gone unanswered long enough to call the connection lost."""
        if not self.stream_started:
            return False  # Nothing is answered before the stream starts.
        now = time.monotonic()
        return any(now - at > timeout_sec for _, at in self._pings.values())

    def clear_pings(self) -> None:
        """Forget the pings sent so far, so the wait for a pong starts now."""
        self._pings.clear()
        self.acked_at = time.monotonic()

    def resend_after(self, last_request: int, token: str) -> list[str | bytes]:
        """
        Take the new connection's word for what it has, and say what to send again.

        The pings of the old connection are gone with it; its pongs would
        confirm messages against a count this stream no longer keeps.
        """
        self.token = token
        self.resumes_without_a_frame += 1
        self._pings.clear()
        self.acked_at = time.monotonic()
        while self._unconfirmed and self._unconfirmed[0][0] <= last_request:
            self._unconfirmed.popleft()
        return [message for _, message in self._unconfirmed]
