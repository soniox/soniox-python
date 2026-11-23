"""
Reconnect: the stream continues on a new connection without losing or
repeating anything.

The bookkeeping is tested on its own, then the session is dropped mid-stream
against a scripted pair of connections.
"""

from __future__ import annotations

import asyncio
import json
import threading
import time
from typing import Any
from unittest.mock import patch

import pytest
from websockets.datastructures import Headers
from websockets.exceptions import ConnectionClosed, InvalidStatus
from websockets.http11 import Response

from soniox.client import AsyncSonioxClient, SonioxClient
from soniox.errors import SonioxRealtimeError
from soniox.realtime._reconnect import (
    MAX_RESUMES_WITHOUT_A_FRAME,
    Ending,
    Reconnect,
)
from soniox.types.realtime import RealtimeSTTConfig

from .mock_ws import AsyncMockWebSocket, MockWebSocket

CONFIG = RealtimeSTTConfig(model="stt-rt-v6", audio_format="auto", enable_reconnect=True)

RECONNECT = {
    "type": "reconnect",
    "reconnect_token": "token-1",
    "reconnect_url": "wss://stt-rt.soniox.com/transcribe-websocket?reconnect=true",
}


def _tokens(text: str, seq: int) -> dict:
    return {"tokens": [{"text": text, "start_ms": 0, "end_ms": 100}], "seq": seq}


def _heard(socket: MockWebSocket | AsyncMockWebSocket, counted: int = -1) -> list[Any]:
    """
    What the server got on a connection, without the request that opened it.

    `counted` is how many of our messages it had when the connection went away,
    so the rest are the ones it never saw.
    """
    messages = socket.sent_messages[1:]
    return messages if counted < 0 else messages[:counted]


# ---------------------------------------------------------------------------
# Bookkeeping
# ---------------------------------------------------------------------------


def test_a_pong_confirms_the_messages_sent_before_its_ping() -> None:
    state = Reconnect()
    state.record(b"one")
    ping = state.ping()
    state.record(b"two")

    state.pong(int(ping.split('"id": ')[1].rstrip("}")))

    # "one" was confirmed, "two" was still in flight when the ping went out.
    assert state.resend_after(0, "token-2") == [b"two"]


def test_a_pong_is_when_the_server_last_had_our_messages() -> None:
    """The reconnect window is counted from this, so a pong has to move it."""
    with patch("soniox.realtime._reconnect.time.monotonic", side_effect=[0.0, 1.0, 5.0]):
        state = Reconnect()  # Created at 0.0.
        state.ping()  # Sent at 1.0.
        state.pong(1)  # Answered at 5.0.

    assert state.acked_at == 5.0


def test_an_unanswered_pong_is_only_overdue_after_its_timeout() -> None:
    state = Reconnect()
    state.stream_started = True  # Before that, nothing is answered.
    state.ping()
    assert not state.pong_overdue(5.0)
    assert state.pong_overdue(0.0)


def test_a_pong_is_not_owed_until_the_stream_starts() -> None:
    """The server answers a ping sent with the start request only once it has."""
    state = Reconnect()
    state.ping()

    assert not state.pong_overdue(0.0)

    state.stream_started = True
    assert state.pong_overdue(0.0)


def test_taking_over_resends_what_the_server_did_not_get() -> None:
    state = Reconnect()
    for chunk in (b"one", b"two", b"three"):
        state.record(chunk)

    assert state.resend_after(1, "token-2") == [b"two", b"three"]
    assert state.token == "token-2"


def test_a_stream_without_a_token_cannot_be_taken_over(client: SonioxClient) -> None:
    """Whether a stream can be continued is the session's own question now.

    It needs both halves: somewhere to dial, and an ending that has not
    happened yet.
    """
    session = client.realtime.stt.connect(config=CONFIG)
    state = session._reconnect  # pyright: ignore[reportPrivateUsage]
    assert state is not None
    assert not session._can_resume()  # pyright: ignore[reportPrivateUsage]

    state.url = "wss://example.test"
    assert session._can_resume()  # pyright: ignore[reportPrivateUsage]

    for ending in Ending:
        session._over = ending  # pyright: ignore[reportPrivateUsage]
        assert not session._can_resume(), ending  # pyright: ignore[reportPrivateUsage]


# ---------------------------------------------------------------------------
# The session
# ---------------------------------------------------------------------------


def test_a_dropped_connection_continues_the_stream_and_resends(client: SonioxClient) -> None:
    dropped, resumed = MockWebSocket(), MockWebSocket()
    dropped.push_recv(RECONNECT)
    dropped.push_recv(_tokens("one", 1))
    dropped.push_recv_error(ConnectionClosed(None, None))
    resumed.push_recv({"type": "reconnected", "reconnect_token": "token-2", "last_request": 1})
    resumed.push_recv(_tokens("one", 1))  # Replayed, the caller already has it.
    resumed.push_recv(_tokens("two", 2))
    resumed.push_recv({"finished": True})
    resumed.close_after_recv()

    with patch("soniox.realtime.stt.sync_ws_connect", side_effect=[dropped, resumed]) as connect:
        with client.realtime.stt.connect(config=CONFIG) as session:
            session.send_byte_chunk(b"first")
            session.send_byte_chunk(b"second")
            received = list(session.receive_events())

    # The token message and the replayed result do not reach the caller; the
    # `reconnected` message does, so the caller knows the stream dropped.
    assert [event.type for event in received] == [None, "reconnected", None, None]
    assert [token.text for event in received for token in event.tokens] == ["one", "two"]
    assert connect.call_args_list[1].args[0] == RECONNECT["reconnect_url"]
    assert resumed.sent_messages[0] == {
        "type": "reconnect",
        "reconnect_token": "token-1",
        "last_seq": 1,
    }
    # The second chunk is the one the server had not counted.
    assert resumed.sent_messages[1] == b"second"


def test_the_caller_is_told_the_stream_dropped_and_came_back(client: SonioxClient) -> None:
    dropped, resumed = MockWebSocket(), MockWebSocket()
    dropped.push_recv(RECONNECT)
    dropped.push_recv_error(ConnectionClosed(None, None))
    resumed.push_recv({"type": "reconnected", "reconnect_token": "token-2", "last_request": 0})
    resumed.close_after_recv()

    with patch("soniox.realtime.stt.sync_ws_connect", side_effect=[dropped, resumed]):
        with client.realtime.stt.connect(config=CONFIG) as session:
            event = session.receive_event()

    assert event is not None
    assert event.type == "reconnected"
    assert event.last_request == 0
    assert event.tokens == []


def test_a_refused_reconnect_says_why(client: SonioxClient) -> None:
    dropped, refusing = MockWebSocket(), MockWebSocket()
    dropped.push_recv(RECONNECT)
    dropped.push_recv_error(ConnectionClosed(None, None))
    refusing.push_recv(
        {
            "error_code": 400,
            "error_message": "The stream has ended. Start a new stream.",
        }
    )

    with patch("soniox.realtime.stt.sync_ws_connect", side_effect=[dropped, refusing]):
        with client.realtime.stt.connect(config=CONFIG) as session:
            with pytest.raises(SonioxRealtimeError, match="The stream has ended"):
                list(session.receive_events())

    assert refusing.aborted  # A close frame is for a stream we are leaving behind.


def test_a_reconnect_refused_at_the_handshake_says_why(client: SonioxClient) -> None:
    """An expired temporary key is a 401 on the handshake, not a refusal frame."""
    dropped = MockWebSocket()
    dropped.push_recv(RECONNECT)
    dropped.push_recv_error(ConnectionClosed(None, None))
    refusal = InvalidStatus(Response(401, "Unauthorized", Headers()))

    with patch("soniox.realtime.stt.sync_ws_connect", side_effect=[dropped, refusal]):
        with client.realtime.stt.connect(config=CONFIG) as session:
            with pytest.raises(SonioxRealtimeError, match="HTTP 401"):
                list(session.receive_events())


def test_a_way_in_that_is_restarting_is_dialled_again(client: SonioxClient) -> None:
    """A 5xx on the handshake is the way in being down, not a refusal.

    The way in can answer 503 while the stream itself is
    still there, and that is the commonest reason a reconnect happens at all.
    """
    dropped, resumed = MockWebSocket(), MockWebSocket()
    dropped.push_recv(RECONNECT)
    dropped.push_recv_error(ConnectionClosed(None, None))
    resumed.push_recv({"type": "reconnected", "reconnect_token": "token-2", "last_request": 1})
    resumed.push_recv({"finished": True})
    resumed.close_after_recv()
    busy = InvalidStatus(Response(503, "Service Unavailable", Headers()))

    with (
        patch("soniox.realtime.stt.sync_ws_connect", side_effect=[dropped, busy, resumed]),
        patch("soniox.realtime.stt.time.sleep"),
    ):
        with client.realtime.stt.connect(config=CONFIG) as session:
            received = list(session.receive_events())

    assert [event.type for event in received] == ["reconnected", None]


def test_a_dial_that_is_never_answered_is_let_go(client: SonioxClient) -> None:
    """Three unanswered dials must not leave three connections open.

    Nothing else holds them, the server counts them against our connection
    limit, and the docs say to drop the connection before trying again.
    """
    dropped = MockWebSocket()
    dropped.push_recv(RECONNECT)
    dropped.push_recv_error(ConnectionClosed(None, None))
    config = CONFIG.model_copy(update={"idle_timeout_ms": 4000})
    dials: list[MockWebSocket] = []

    def dial(*_args: Any, **_kwargs: Any) -> MockWebSocket:
        if not dials:
            dials.append(dropped)
            return dropped
        silent = MockWebSocket()
        silent.push_recv_error(TimeoutError())
        dials.append(silent)
        return silent

    with (
        patch("soniox.realtime.stt.sync_ws_connect", side_effect=dial),
        patch("soniox.realtime.stt.time.sleep"),
    ):
        with client.realtime.stt.connect(config=config) as session:
            with pytest.raises(SonioxRealtimeError, match="window closed"):
                list(session.receive_events())

    assert dials[1:], "no dial was attempted"
    assert all(ws.aborted for ws in dials[1:]), "a connection was left open"


def test_the_stream_is_not_taken_from_the_connection_that_has_it(
    client: SonioxClient,
) -> None:
    """`connection_replaced` says someone else holds the stream, not that it ended.

    Dialling would take it from them, and a close frame on this socket would
    end the stream they are using.
    """
    ws = MockWebSocket()
    ws.push_recv(RECONNECT)
    ws.push_recv(
        {
            "error_code": 400,
            "error_type": "connection_replaced",
            "error_message": "The connection was replaced by a new one.",
        }
    )
    ws.close_after_recv()  # The server has already left this connection behind.

    with patch("soniox.realtime.stt.sync_ws_connect", side_effect=[ws]) as connect:
        with client.realtime.stt.connect(config=CONFIG) as session:
            received = list(session.receive_events())

    assert connect.call_count == 1, "the stream was dialled for while another connection had it"
    assert [event.error_type for event in received] == ["connection_replaced"]
    assert ws.aborted and not ws.ended_by_us, "a close frame would have ended their stream"


def test_the_wait_for_a_pong_starts_when_the_stream_does(client: SonioxClient) -> None:
    """A ping sent before the stream started is answered once it starts.

    Its pong looks late by then, and an unanswered ping is what the session
    takes for a lost connection - so the frame that starts the stream is where
    the waiting begins.
    """
    ws = MockWebSocket()
    ws.push_recv(RECONNECT)
    ws.push_recv({"finished": True})
    ws.close_after_recv()

    with patch("soniox.realtime.stt.sync_ws_connect", side_effect=[ws]):
        with client.realtime.stt.connect(config=CONFIG) as session:
            state = session._reconnect  # pyright: ignore[reportPrivateUsage]
            assert state is not None
            state.ping()  # Sent while the server was still starting the stream.
            session.receive_event()  # The frame that starts it.
            # Nothing is outstanding, so no timeout can be overdue.
            assert not state.pong_overdue(0.0), "a ping from before the stream is still waiting"
            list(session.receive_events())


def test_a_terminal_frame_ends_the_stream_whatever_its_number(
    client: SonioxClient,
) -> None:
    """The replay drops what the caller has seen, and a terminal frame is not that.

    The server's last frame can be numbered behind the replay, or carry no
    number at all, and either way it is the end.
    """
    for terminal in ({"finished": True, "seq": 1}, {"finished": True}):
        ws = MockWebSocket()
        ws.push_recv(RECONNECT)
        ws.push_recv(_tokens("one", 7))
        ws.push_recv(terminal)
        ws.close_after_recv()

        with patch("soniox.realtime.stt.sync_ws_connect", side_effect=[ws]):
            with client.realtime.stt.connect(config=CONFIG) as session:
                received = list(session.receive_events())

        assert [event.finished for event in received] == [False, True], terminal


def test_an_error_code_of_zero_is_not_an_error(client: SonioxClient) -> None:
    """Only a non-zero code ends the stream; zero is a field that was sent anyway.

    A stream taken as ended is a stream nothing dials for again, so the drop
    after the frame is what tells the two apart.
    """
    dropped, resumed = MockWebSocket(), MockWebSocket()
    dropped.push_recv(RECONNECT)
    dropped.push_recv({"error_code": 0, **_tokens("one", 1)})
    dropped.push_recv_error(ConnectionClosed(None, None))
    resumed.push_recv({"type": "reconnected", "reconnect_token": "token-2", "last_request": 1})
    resumed.push_recv({"finished": True})
    resumed.close_after_recv()

    with patch("soniox.realtime.stt.sync_ws_connect", side_effect=[dropped, resumed]) as connect:
        with client.realtime.stt.connect(config=CONFIG) as session:
            received = list(session.receive_events())

    assert connect.call_count == 2, "a zero error code was taken for the end of the stream"
    assert [token.text for event in received for token in event.tokens] == ["one"]
    assert received[-1].finished


def test_a_close_with_no_terminal_frame_takes_the_stream_over(client: SonioxClient) -> None:
    """A server going away closes with 1001, which the library calls OK.

    Nothing said the stream was over, so it is still there to be taken over -
    and the transcript would be silently cut short if it were not.
    """
    dropped, resumed = MockWebSocket(), MockWebSocket()
    dropped.push_recv(RECONNECT)
    dropped.push_recv(_tokens("one", 1))
    dropped.close_after_recv()
    resumed.push_recv({"type": "reconnected", "reconnect_token": "token-2", "last_request": 0})
    resumed.push_recv(_tokens("two", 2))
    resumed.push_recv({"finished": True})
    resumed.close_after_recv()

    with patch("soniox.realtime.stt.sync_ws_connect", side_effect=[dropped, resumed]) as connect:
        with client.realtime.stt.connect(config=CONFIG) as session:
            received = list(session.receive_events())

    assert connect.call_count == 2, "the stream was abandoned on an OK close"
    assert [token.text for event in received for token in event.tokens] == ["one", "two"]


def test_a_stream_the_server_offered_no_reconnect_for_just_ends(client: SonioxClient) -> None:
    """No `reconnect` message means the stream cannot be continued."""
    ws = MockWebSocket()
    ws.push_recv(_tokens("one", 1))
    ws.push_recv_error(ConnectionClosed(None, None))

    with patch("soniox.realtime.stt.sync_ws_connect", side_effect=[ws]) as connect:
        with client.realtime.stt.connect(config=CONFIG) as session:
            received = list(session.receive_events())

    assert connect.call_count == 1, "a stream with no token was dialled for"
    assert [token.text for event in received for token in event.tokens] == ["one"]


def test_the_stream_is_continued_after_the_end_of_audio(client: SonioxClient) -> None:
    """The window where a drop costs the caller the whole transcript.

    The server runs on to its final results after the empty frame, so a socket
    lost in that window is still worth taking over.
    """
    dropped, resumed = MockWebSocket(), MockWebSocket()
    dropped.push_recv(RECONNECT)
    dropped.push_recv_error(ConnectionClosed(None, None))
    resumed.push_recv({"type": "reconnected", "reconnect_token": "token-2", "last_request": 0})
    resumed.push_recv(_tokens("one", 1))
    resumed.push_recv({"finished": True})
    resumed.close_after_recv()

    with patch("soniox.realtime.stt.sync_ws_connect", side_effect=[dropped, resumed]) as connect:
        with client.realtime.stt.connect(config=CONFIG) as session:
            session.finish()
            received = list(session.receive_events())

    assert connect.call_count == 2, "the stream was abandoned after the end of audio"
    assert [token.text for event in received for token in event.tokens] == ["one"]
    # The server had not counted the empty frame, so it goes out again: without
    # it the server never reaches its final results.
    assert "" in resumed.sent_messages, "the end of audio was not sent again"


def test_the_stream_is_not_continued_once_it_has_finished(client: SonioxClient) -> None:
    """A `finished` frame is the end. Nothing dials again after it."""
    ws = MockWebSocket()
    ws.push_recv(RECONNECT)
    ws.push_recv({"finished": True})
    ws.close_after_recv()

    with patch("soniox.realtime.stt.sync_ws_connect", side_effect=[ws]) as connect:
        with client.realtime.stt.connect(config=CONFIG) as session:
            session.finish()
            list(session.receive_events())

    assert connect.call_count == 1


def test_sending_after_the_stream_has_ended_raises(client: SonioxClient) -> None:
    """Otherwise an audio thread keeps filling a resend log nothing will send."""
    ws = MockWebSocket()
    ws.push_recv(RECONNECT)
    ws.push_recv({"finished": True})
    ws.close_after_recv()

    with patch("soniox.realtime.stt.sync_ws_connect", side_effect=[ws]):
        with client.realtime.stt.connect(config=CONFIG) as session:
            list(session.receive_events())
            with pytest.raises(SonioxRealtimeError, match="has ended"):
                session.send_byte_chunk(b"late")


def test_the_end_of_audio_is_sent_once(client: SonioxClient) -> None:
    ws = MockWebSocket()
    ws.push_recv(RECONNECT)

    with patch("soniox.realtime.stt.sync_ws_connect", return_value=ws):
        with client.realtime.stt.connect(config=CONFIG) as session:
            session.finish()
            session.finish()  # Nor may saying it again, or closing the session.

    assert [m for m in ws.sent_messages if m == ""] == [""]


def test_a_silent_drop_is_noticed_by_the_unanswered_ping(client: SonioxClient) -> None:
    silent, resumed = MockWebSocket(), MockWebSocket()
    silent.push_recv(RECONNECT)
    silent.go_silent()
    resumed.push_recv({"type": "reconnected", "reconnect_token": "token-2", "last_request": 0})
    resumed.push_recv(_tokens("one", 1))
    resumed.push_recv({"finished": True})
    resumed.close_after_recv()

    with patch("soniox.realtime.stt.sync_ws_connect", side_effect=[silent, resumed]):
        session = client.realtime.stt.connect(config=CONFIG)
        session._ping_interval_sec = 0.05  # pyright: ignore[reportPrivateUsage]
        with session:
            received = list(session.receive_events())

    assert [token.text for event in received for token in event.tokens] == ["one"]
    assert silent.aborted  # Dropped without a close frame, which would end the stream.


def test_the_ping_log_is_only_read_with_the_lock_held(client: SonioxClient) -> None:
    """Two threads use this log: the ping thread writes it, the reader reads it.

    `ping()` is called under the session's lock, so the overdue check has to
    take it as well. Without it the two meet mid-iteration and the read raises
    `RuntimeError: dictionary changed size during iteration`.
    """
    silent = MockWebSocket()
    silent.push_recv(RECONNECT)
    silent.go_silent()
    held: list[bool] = []

    with patch("soniox.realtime.stt.sync_ws_connect", return_value=silent):
        with client.realtime.stt.connect(config=CONFIG) as session:
            state = session._reconnect  # pyright: ignore[reportPrivateUsage]
            assert state is not None
            state.stream_started = True  # The check does nothing before that.
            lock = session._lock  # pyright: ignore[reportPrivateUsage]
            reads_the_log = state.pong_overdue

            def watched(timeout_sec: float) -> bool:
                held.append(lock.locked())
                return reads_the_log(timeout_sec)

            state.pong_overdue = watched  # pyright: ignore[reportAttributeAccessIssue]
            assert session.recv_bytes()  # The token message.
            session._ping_interval_sec = 0.0  # pyright: ignore[reportPrivateUsage]
            state.ping()
            # `recv_bytes` records nothing, so this stream has no token of its
            # own: the drop cannot be taken over, and that is a lost connection.
            with pytest.raises(SonioxRealtimeError, match="ping went unanswered"):
                session.recv_bytes()

    assert held, "the ping log was never read, so nothing was tested"
    assert all(held), f"the log was read without the lock: {held}"


def test_pings_are_not_counted_as_messages_to_resend(client: SonioxClient) -> None:
    dropped, resumed = MockWebSocket(), MockWebSocket()
    dropped.push_recv(RECONNECT)
    dropped.push_recv({"type": "pong", "id": 1})
    dropped.push_recv_error(ConnectionClosed(None, None))
    resumed.push_recv({"type": "reconnected", "reconnect_token": "token-2", "last_request": 0})
    resumed.push_recv({"finished": True})
    resumed.close_after_recv()

    with patch("soniox.realtime.stt.sync_ws_connect", side_effect=[dropped, resumed]):
        session = client.realtime.stt.connect(config=CONFIG)
        session._ping_interval_sec = 0.01  # pyright: ignore[reportPrivateUsage]
        with session:
            session.send_byte_chunk(b"audio")
            # The `reconnected` message and the end of the stream: the pong is
            # kept to ourselves.
            assert [event.type for event in session.receive_events()] == ["reconnected", None]

    assert [m for m in resumed.sent_messages if isinstance(m, bytes)] == [b"audio"]


def test_a_pinging_session_does_not_also_send_for_calleralives(client: SonioxClient) -> None:
    """One timer, not two: a ping already holds the stream open.

    The docs say so outright, and a paused session that pings was starting a
    second thread to send a message the ping had covered.
    """
    ws = MockWebSocket()
    ws.push_recv(RECONNECT)
    ws.close_after_recv()

    with patch("soniox.realtime.stt.sync_ws_connect", side_effect=[ws]):
        with client.realtime.stt.connect(config=CONFIG) as session:
            session.pause(finalize=False)
            assert session.paused
            keepalive = session._for_calleralive  # pyright: ignore[reportPrivateUsage]
            ping = session._ping  # pyright: ignore[reportPrivateUsage]
            session.resume()

    assert keepalive is None, "a pinging session started a keepalive beside its ping"
    assert ping is not None, "the ping that holds the stream open was not running"


def test_a_session_without_reconnect_does_not_ping(client: SonioxClient) -> None:
    ws = MockWebSocket()
    ws.close_after_recv()
    config = RealtimeSTTConfig(model="stt-rt-v6", audio_format="auto")

    with patch("soniox.realtime.stt.sync_ws_connect", return_value=ws):
        with client.realtime.stt.connect(config=config) as session:
            assert list(session.receive_events()) == []

    assert not any(isinstance(m, dict) and m.get("type") == "ping" for m in ws.sent_messages)


@pytest.mark.parametrize(
    ("idle_timeout_ms", "expected_sec"),
    [(None, 2.0), (20000, 2.0), (8000, 2.0), (3000, 0.75)],
)
def test_the_pings_are_paced_by_the_idle_timeout(
    client: SonioxClient, idle_timeout_ms: int | None, expected_sec: float
) -> None:
    # 2s each, as the docs ask, until the caller shortens the idle timeout
    # below 8s: a ping restarts that timeout, so both have to fit inside it.
    config = CONFIG.model_copy(update={"idle_timeout_ms": idle_timeout_ms})
    session = client.realtime.stt.connect(config=config)

    assert session._ping_interval_sec == expected_sec  # pyright: ignore[reportPrivateUsage]
    # A ping and the wait for its pong both have to fit inside the window.
    assert 2 * session._ping_interval_sec < session._idle_timeout_sec  # pyright: ignore[reportPrivateUsage]


def test_each_reconnect_uses_the_newest_token(client: SonioxClient) -> None:
    """Every `reconnected` reply carries a new token; the old one is spent."""
    first, second, third = MockWebSocket(), MockWebSocket(), MockWebSocket()
    first.push_recv(RECONNECT)
    first.push_recv_error(ConnectionClosed(None, None))
    second.push_recv({"type": "reconnected", "reconnect_token": "token-2", "last_request": 0})
    second.push_recv_error(ConnectionClosed(None, None))
    third.push_recv({"type": "reconnected", "reconnect_token": "token-3", "last_request": 0})
    third.push_recv({"finished": True})
    third.close_after_recv()

    with patch("soniox.realtime.stt.sync_ws_connect", side_effect=[first, second, third]):
        with client.realtime.stt.connect(config=CONFIG) as session:
            list(session.receive_events())

    assert second.sent_messages[0]["reconnect_token"] == "token-1"
    assert third.sent_messages[0]["reconnect_token"] == "token-2"


def test_a_reconnect_mid_stream_leaves_the_server_with_what_was_sent(
    client: SonioxClient,
) -> None:
    """The server does not dedup resent audio, and audio frames carry no id.

    Too much and it transcribes the same audio twice, too little and there is a
    gap - so what the server heard across both connections has to be exactly
    what a run with no drop would have delivered, once each and in order.
    """
    chunks = [b"a1", b"a2", b"a3", b"a4"]
    sent: list[str | bytes] = [*chunks, ""]  # What a run with no drop delivers.
    counted = 2  # What the server had when the connection went away.
    dropped, resumed = MockWebSocket(), MockWebSocket()
    dropped.push_recv(RECONNECT)
    dropped.push_recv_error(ConnectionClosed(None, None))
    resumed.push_recv(
        {"type": "reconnected", "reconnect_token": "token-2", "last_request": counted}
    )
    resumed.push_recv({"finished": True})
    resumed.close_after_recv()

    with patch("soniox.realtime.stt.sync_ws_connect", side_effect=[dropped, resumed]):
        with client.realtime.stt.connect(config=CONFIG) as session:
            for chunk in chunks:
                session.send_byte_chunk(chunk)
            session.finish()
            list(session.receive_events())

    assert _heard(dropped, counted) + _heard(resumed) == sent


def test_a_dial_cannot_spend_the_whole_reconnect_window(client: SonioxClient) -> None:
    """A dial that hangs must leave budget for another try.

    The clock here is the dial's own: every attempt and every wait between them
    spends exactly as long as it was given, which is what a server that answers
    nothing at all does. The window is 4s and the caller's connect timeout is
    the default 10s, so only the window can bound an attempt.
    """
    dropped = MockWebSocket()
    dropped.push_recv(RECONNECT)
    dropped.push_recv_error(ConnectionClosed(None, None))
    config = CONFIG.model_copy(update={"idle_timeout_ms": 4000})
    now = [0.0]
    timeouts: list[float] = []
    dials = 0

    def dial(*_args: Any, **kwargs: Any) -> MockWebSocket:
        nonlocal dials
        dials += 1
        if dials == 1:
            return dropped  # The connection the stream started on.
        timeouts.append(kwargs["open_timeout"])
        now[0] += kwargs["open_timeout"]
        raise TimeoutError

    with (
        patch("soniox.realtime.stt.sync_ws_connect", side_effect=dial),
        patch(
            "soniox.realtime.stt.time.sleep",
            side_effect=lambda sec: now.__setitem__(0, now[0] + sec),
        ),
        patch("soniox.realtime.stt.time.monotonic", side_effect=lambda: now[0]),
    ):
        with client.realtime.stt.connect(config=config) as session:
            with pytest.raises(SonioxRealtimeError, match="window closed"):
                list(session.receive_events())

    assert timeouts, "no dial was attempted"
    assert timeouts[0] <= 4.0 / 2, f"the first dial was given {timeouts[0]}s of a 4s window"
    assert len(timeouts) >= 3, f"a hanging dial spent the window: {timeouts}"


def test_a_stream_can_be_continued_more_times_than_a_token_may_be_used(
    client: SonioxClient,
) -> None:
    """The server's three uses are per token, and every takeover brings a new one.

    A flaky network drops a stream more than three times, and each of those is
    a fresh token, so none of them is near the limit.
    """
    drops = 4
    sockets: list[MockWebSocket] = []
    for n in range(drops + 1):
        ws = MockWebSocket()
        if n == 0:
            ws.push_recv(RECONNECT)
        else:
            ws.push_recv(
                {"type": "reconnected", "reconnect_token": f"token-{n + 1}", "last_request": 1}
            )
        if n == drops:
            ws.push_recv({"finished": True})
            ws.close_after_recv()
        else:
            ws.push_recv_error(ConnectionClosed(None, None))
        sockets.append(ws)

    with patch("soniox.realtime.stt.sync_ws_connect", side_effect=sockets) as connect:
        with client.realtime.stt.connect(config=CONFIG) as session:
            events = list(session.receive_events())

    assert connect.call_count == drops + 1
    assert [e.type for e in events] == ["reconnected"] * drops + [None]
    # Each dial carried the token the takeover before it handed over.
    presented = [ws.sent_messages[0]["reconnect_token"] for ws in sockets[1:]]
    assert presented == [f"token-{n}" for n in range(1, drops + 1)]


def test_closing_a_session_ends_the_stream(client: SonioxClient) -> None:
    """A closed session must not leave the stream waiting to be taken over.

    The wait is one idle timeout, and the server bills it on wall clock and
    keeps a concurrent request slot for it, so the close has to say the stream
    is over rather than abandon the socket.
    """
    ws = MockWebSocket()
    ws.push_recv(RECONNECT)
    ws.push_recv({"finished": True})
    ws.close_after_recv()

    with patch("soniox.realtime.stt.sync_ws_connect", side_effect=[ws]):
        with client.realtime.stt.connect(config=CONFIG) as session:
            session.finish()
            list(session.receive_events())

    assert ws.ended_by_us == 1, "the socket was abandoned, so the stream waits its timeout out"
    assert not ws.aborted, "an abandoned socket does not end the stream"


def test_a_token_the_server_will_not_take_again_says_so(client: SonioxClient) -> None:
    """How often a token may be presented is the server's rule, not ours.

    An attempt whose reply never arrives may have been accepted all the same,
    so the session cannot tell when a token is spent. It keeps presenting the
    one it holds while the window lasts, and the refusal, when it comes, is the
    server's own words rather than a guess of ours.
    """
    dropped = MockWebSocket()
    dropped.push_recv(RECONNECT)
    dropped.push_recv_error(ConnectionClosed(None, None))
    presented: list[Any] = []

    def dial(*_args: Any, **_kwargs: Any) -> MockWebSocket:
        if not presented:
            presented.append(dropped)
            return dropped  # The connection the stream started on.
        socket = MockWebSocket()
        if len(presented) < 3:
            socket.push_recv_error(TimeoutError())  # The reply never comes.
        else:
            socket.push_recv(
                {
                    "error_code": 400,
                    "error_type": "reconnect_failed",
                    "error_message": "The reconnect token was used too many times.",
                }
            )
        presented.append(socket)
        return socket

    with (
        patch("soniox.realtime.stt.sync_ws_connect", side_effect=dial),
        patch("soniox.realtime.stt.time.sleep"),
    ):
        with client.realtime.stt.connect(config=CONFIG) as session:
            with pytest.raises(SonioxRealtimeError, match="used too many times"):
                list(session.receive_events())

    # Only the reconnect request on each, and the refusal ended it.
    for socket in presented[1:]:
        assert [m.get("type") for m in socket.sent_messages] == ["reconnect"]


def test_the_wait_between_dials_is_jittered(client: SonioxClient) -> None:
    """Clients dropped at the same moment must not dial again together.

    Equal jitter, so a wait is between half the backoff and all of it. The two
    ends of `random()` are what pin that down: with no jitter both would be the
    whole 250ms.
    """

    def first_wait(roll: float) -> float:
        """The first wait between dials, with `random()` fixed at `roll`."""
        dropped = MockWebSocket()
        dropped.push_recv(RECONNECT)
        dropped.push_recv_error(ConnectionClosed(None, None))
        now = [0.0]
        waits: list[float] = []
        dials = [0]

        def dial(*_args: Any, **_kwargs: Any) -> MockWebSocket:
            dials[0] += 1
            if dials[0] == 1:
                return dropped  # The connection the stream started on.
            raise TimeoutError  # Nothing answers at all.

        def wait(sec: float) -> None:
            waits.append(round(sec, 4))
            now[0] += sec

        config = CONFIG.model_copy(update={"idle_timeout_ms": 3000})
        with (
            patch("soniox.realtime.stt.sync_ws_connect", side_effect=dial),
            patch("soniox.realtime.stt.random.random", return_value=roll),
            patch("soniox.realtime.stt.time.sleep", side_effect=wait),
            patch("soniox.realtime.stt.time.monotonic", side_effect=lambda: now[0]),
        ):
            with client.realtime.stt.connect(config=config) as session:
                with pytest.raises(SonioxRealtimeError):
                    list(session.receive_events())
        assert waits, "no dial was retried"
        return waits[0]

    assert first_wait(0.0) == 0.125, "the shortest wait is half the backoff"
    assert first_wait(1.0) == 0.25, "the longest wait is all of it"


def test_a_closed_session_does_not_continue_the_stream(client: SonioxClient) -> None:
    """Closing is the end of the stream, whatever the session was in the middle of."""
    ws = MockWebSocket()
    ws.push_recv(RECONNECT)
    ws.push_recv(_tokens("one", 1))

    with patch("soniox.realtime.stt.sync_ws_connect", side_effect=[ws]) as connect:
        with client.realtime.stt.connect(config=CONFIG) as session:
            session.receive_event()  # Takes the token, so the stream could resume.
            session.close()
            assert session._continue_stream() is None  # pyright: ignore[reportPrivateUsage]

    assert connect.call_count == 1, "a closed session went looking for its stream"
    assert ws.ended_by_us == 1, "the stream was left to wait out its idle timeout"


def test_the_window_is_counted_from_the_last_answered_ping(client: SonioxClient) -> None:
    """The server's window is already running from the last message it got.

    On a silent drop that is a ping and a pong before we noticed, so counting
    from the drop would keep dialling after the server has freed the stream.
    """
    dropped = MockWebSocket()
    dropped.push_recv(RECONNECT)
    dropped.push_recv(_tokens("one", 1))
    dropped.push_recv_error(ConnectionClosed(None, None))
    now = [0.0]
    dials = [0]

    def dial(*_args: Any, **_kwargs: Any) -> MockWebSocket:
        dials[0] += 1
        if dials[0] == 1:
            return dropped  # The connection the stream started on.
        raise TimeoutError  # Nothing answers at all.

    def wait(sec: float) -> None:
        now[0] += sec

    config = CONFIG.model_copy(update={"idle_timeout_ms": 4000})
    with (
        patch("soniox.realtime.stt.sync_ws_connect", side_effect=dial),
        patch("soniox.realtime.stt.random.random", return_value=0.0),
        patch("soniox.realtime.stt.time.sleep", side_effect=wait),
        patch("soniox.realtime.stt.time.monotonic", side_effect=lambda: now[0]),
    ):
        with client.realtime.stt.connect(config=config) as session:
            session.receive_event()  # The frame that starts the stream, then a token.
            state = session._reconnect  # pyright: ignore[reportPrivateUsage]
            assert state is not None
            # The last pong came in 3s ago, so 1s of the 4s window is left.
            state.acked_at = now[0] - 3.0
            with pytest.raises(SonioxRealtimeError, match="window closed"):
                list(session.receive_events())

    # The last backoff overruns by its own length, so the bound is not the 1s
    # itself - but counting from the drop would give the full 4s and spend it.
    assert now[0] < 3.0, f"the window ran past what the server kept: {now[0]:.2f}s"


def test_closing_in_the_middle_of_a_takeover_still_ends_the_stream(
    client: SonioxClient,
) -> None:
    """A takeover leaves no socket to end the stream on, so one is dialled for it.

    Without it the stream waits out its whole idle timeout, which the caller is
    billed for and which holds a concurrent request slot.
    """
    dropped = MockWebSocket()
    dropped.push_recv(RECONNECT)
    dropped.push_recv(_tokens("one", 1))
    ending = MockWebSocket()
    ending.push_recv({"type": "reconnected", "reconnect_token": "token-2", "last_request": 1})

    with patch("soniox.realtime.stt.sync_ws_connect", side_effect=[dropped, ending]) as connect:
        with client.realtime.stt.connect(config=CONFIG) as session:
            session.receive_event()  # Takes the token, so the stream could resume.
            session._drop_socket()  # pyright: ignore[reportPrivateUsage]
            session.close()

    assert connect.call_count == 2, "nothing was dialled, so the stream was left running"
    assert ending.sent_messages[0]["type"] == "reconnect"
    assert ending.ended_by_us == 1, "the stream was taken over and then not ended"


def test_a_session_closed_while_it_dials_lets_the_new_connection_go(
    client: SonioxClient,
) -> None:
    """Keeping it would leave a live stream with nothing pinging or reading it."""
    dropped, resumed = MockWebSocket(), MockWebSocket()
    dropped.push_recv(RECONNECT)
    dropped.push_recv(_tokens("one", 1))
    dropped.push_recv_error(ConnectionClosed(None, None))
    resumed.push_recv({"type": "reconnected", "reconnect_token": "token-2", "last_request": 0})

    session = client.realtime.stt.connect(config=CONFIG)
    dialled: list[MockWebSocket] = []

    def dial(*_args: object, **_kwargs: object) -> MockWebSocket:
        dialled.append(MockWebSocket())
        if len(dialled) == 1:
            return dropped
        if len(dialled) == 2:
            session.close()  # The caller is done while the reconnect is in flight.
            return resumed
        # Closing dials once more to end the stream; that is its own test.
        return dialled[-1]

    with patch("soniox.realtime.stt.sync_ws_connect", side_effect=dial):
        with session:
            received = list(session.receive_events())

    assert [token.text for event in received for token in event.tokens] == ["one"]
    # This connection has the stream, so closing it is what ends the stream.
    # Letting it go would leave the stream waiting out its idle timeout.
    assert resumed.ended_by_us >= 1, "the stream was left running on a closed session"


async def test_a_dropped_connection_continues_the_stream_async(
    async_client: AsyncSonioxClient,
) -> None:
    dropped, resumed = AsyncMockWebSocket(), AsyncMockWebSocket()
    dropped.push_recv(RECONNECT)
    dropped.push_recv(_tokens("one", 1))
    dropped.push_recv_error(ConnectionClosed(None, None))
    resumed.push_recv({"type": "reconnected", "reconnect_token": "token-2", "last_request": 1})
    resumed.push_recv(_tokens("one", 1))  # Replayed, the caller already has it.
    resumed.push_recv(_tokens("two", 2))
    resumed.push_recv({"finished": True})
    resumed.close_after_recv()

    with patch("soniox.realtime.async_stt.async_ws_connect", side_effect=[dropped, resumed]):
        async with async_client.realtime.stt.connect(config=CONFIG) as session:
            await session.send_byte_chunk(b"first")
            await session.send_byte_chunk(b"second")
            received = [event async for event in session.receive_events()]

    assert [token.text for event in received for token in event.tokens] == ["one", "two"]
    assert resumed.sent_messages[0] == {
        "type": "reconnect",
        "reconnect_token": "token-1",
        "last_seq": 1,
    }
    assert resumed.sent_messages[1] == b"second"


def test_audio_sent_during_a_takeover_is_kept(client: SonioxClient) -> None:
    # The window the resend log exists for: the old socket is gone, the new one
    # is not up yet, and the caller's audio thread is still sending.
    ws = MockWebSocket()
    ws.push_recv(RECONNECT)
    ws.push_recv(_tokens("one", 1))

    with patch("soniox.realtime.stt.sync_ws_connect", return_value=ws):
        with client.realtime.stt.connect(config=CONFIG) as session:
            session.receive_event()  # Takes the token, so the stream can resume.
            session._drop_socket()  # pyright: ignore[reportPrivateUsage]

            session.send_byte_chunk(b"during")

            state = session._reconnect  # pyright: ignore[reportPrivateUsage]
            assert state is not None
            assert state.resend_after(0, "token-2") == [b"during"]


async def test_a_close_with_no_terminal_frame_takes_the_stream_over_async(
    async_client: AsyncSonioxClient,
) -> None:
    dropped, resumed = AsyncMockWebSocket(), AsyncMockWebSocket()
    dropped.push_recv(RECONNECT)
    dropped.push_recv(_tokens("one", 1))
    dropped.close_after_recv()
    resumed.push_recv({"type": "reconnected", "reconnect_token": "token-2", "last_request": 0})
    resumed.push_recv(_tokens("two", 2))
    resumed.push_recv({"finished": True})
    resumed.close_after_recv()

    with patch(
        "soniox.realtime.async_stt.async_ws_connect", side_effect=[dropped, resumed]
    ) as connect:
        async with async_client.realtime.stt.connect(config=CONFIG) as session:
            received = [event async for event in session.receive_events()]

    assert connect.call_count == 2, "the stream was abandoned on an OK close"
    assert [token.text for event in received for token in event.tokens] == ["one", "two"]


async def test_a_refused_reconnect_says_why_async(async_client: AsyncSonioxClient) -> None:
    dropped, refusing = AsyncMockWebSocket(), AsyncMockWebSocket()
    dropped.push_recv(RECONNECT)
    dropped.push_recv_error(ConnectionClosed(None, None))
    refusing.push_recv(
        {
            "error_code": 400,
            "error_message": "The stream has ended. Start a new stream.",
        }
    )

    with patch("soniox.realtime.async_stt.async_ws_connect", side_effect=[dropped, refusing]):
        async with async_client.realtime.stt.connect(config=CONFIG) as session:
            with pytest.raises(SonioxRealtimeError, match="The stream has ended"):
                [event async for event in session.receive_events()]

    # Abandoned, not closed: a close handshake on a refused socket can stall.
    assert refusing.aborted


async def test_a_reconnect_refused_at_the_handshake_says_why_async(
    async_client: AsyncSonioxClient,
) -> None:
    dropped = AsyncMockWebSocket()
    dropped.push_recv(RECONNECT)
    dropped.push_recv_error(ConnectionClosed(None, None))
    refusal = InvalidStatus(Response(401, "Unauthorized", Headers()))

    with patch("soniox.realtime.async_stt.async_ws_connect", side_effect=[dropped, refusal]):
        async with async_client.realtime.stt.connect(config=CONFIG) as session:
            with pytest.raises(SonioxRealtimeError, match="HTTP 401"):
                [event async for event in session.receive_events()]


async def test_sending_after_the_stream_has_ended_raises_async(
    async_client: AsyncSonioxClient,
) -> None:
    ws = AsyncMockWebSocket()
    ws.push_recv(RECONNECT)
    ws.push_recv({"finished": True})
    ws.close_after_recv()

    with patch("soniox.realtime.async_stt.async_ws_connect", side_effect=[ws]):
        async with async_client.realtime.stt.connect(config=CONFIG) as session:
            [event async for event in session.receive_events()]
            with pytest.raises(SonioxRealtimeError, match="has ended"):
                await session.send_byte_chunk(b"late")


async def test_the_stream_is_not_taken_from_the_connection_that_has_it_async(
    async_client: AsyncSonioxClient,
) -> None:
    ws = AsyncMockWebSocket()
    ws.push_recv(RECONNECT)
    ws.push_recv(
        {
            "error_code": 400,
            "error_type": "connection_replaced",
            "error_message": "The connection was replaced by a new one.",
        }
    )
    ws.close_after_recv()  # The server has already left this connection behind.

    with patch("soniox.realtime.async_stt.async_ws_connect", side_effect=[ws]) as connect:
        async with async_client.realtime.stt.connect(config=CONFIG) as session:
            received = [event async for event in session.receive_events()]

    assert connect.call_count == 1, "the stream was dialled for while another connection had it"
    assert [event.error_type for event in received] == ["connection_replaced"]
    assert ws.aborted and not ws.ended_by_us, "a close frame would have ended their stream"


async def test_one_read_spans_every_bounded_wait(async_client: AsyncSonioxClient) -> None:
    """The wait for a frame is bounded, the read itself is not.

    Each wait is short so an unanswered ping is noticed in seconds, but the
    `recv` behind it has to be the same one every time: a second reader of the
    same socket takes frames the first will never return.
    """
    ws, spare = AsyncMockWebSocket(), AsyncMockWebSocket()
    ws.push_recv(RECONNECT)
    reads = [0]

    async def hangs(timeout: float | None = None) -> str:
        _ = timeout
        reads[0] += 1
        await asyncio.Event().wait()
        raise AssertionError("unreachable")

    with patch("soniox.realtime.async_stt.async_ws_connect", side_effect=[ws, spare]):
        async with async_client.realtime.stt.connect(config=CONFIG) as session:
            assert await session.recv_bytes()  # The token message.
            ws.recv = hangs  # pyright: ignore[reportAttributeAccessIssue]
            session._ping_interval_sec = 0.001  # pyright: ignore[reportPrivateUsage]
            reading = asyncio.ensure_future(session.recv_bytes())
            await asyncio.sleep(0.05)  # Many bounded waits go by with no frame.
            reading.cancel()

    assert reads[0] == 1, f"the socket was read {reads[0]} times over one wait"


async def test_a_silent_drop_is_noticed_by_the_unanswered_ping_async(
    async_client: AsyncSonioxClient,
) -> None:
    """A dropped connection often arrives as nothing at all.

    The session reuses one pending `recv` across its bounded waits, so this is
    also what proves that waiting again does not lose the frame or the task.
    """
    silent, resumed = AsyncMockWebSocket(), AsyncMockWebSocket()
    silent.push_recv(RECONNECT)
    silent.go_silent()
    resumed.push_recv({"type": "reconnected", "reconnect_token": "token-2", "last_request": 1})
    resumed.push_recv(_tokens("one", 1))
    resumed.push_recv({"finished": True})
    resumed.close_after_recv()
    config = CONFIG.model_copy(update={"idle_timeout_ms": 3000})

    with patch("soniox.realtime.async_stt.async_ws_connect", side_effect=[silent, resumed]) as c:
        async with async_client.realtime.stt.connect(config=config) as session:
            state = session._reconnect  # pyright: ignore[reportPrivateUsage]
            assert state is not None
            # A ping of our own, already overdue, so the silence is noticed on
            # the first wait instead of two real ping intervals later. The
            # frame that starts the stream is read by the iteration below,
            # which is what records the token.
            state.ping()
            session._ping_interval_sec = 0.0  # pyright: ignore[reportPrivateUsage]
            received = [event async for event in session.receive_events()]

    assert c.call_count == 2, "the silence was never noticed"
    assert [token.text for event in received for token in event.tokens] == ["one"]
    assert silent.aborted, "the silent connection was left open"


async def test_closing_a_session_ends_the_stream_async(
    async_client: AsyncSonioxClient,
) -> None:
    ws = AsyncMockWebSocket()
    ws.push_recv(RECONNECT)
    ws.push_recv({"finished": True})
    ws.close_after_recv()

    with patch("soniox.realtime.async_stt.async_ws_connect", side_effect=[ws]):
        async with async_client.realtime.stt.connect(config=CONFIG) as session:
            await session.finish()
            [event async for event in session.receive_events()]

    assert ws.ended_by_us == 1, "the socket was abandoned, so the stream waits its timeout out"
    assert not ws.aborted, "an abandoned socket does not end the stream"


async def test_audio_sent_during_a_takeover_is_kept_async(
    async_client: AsyncSonioxClient,
) -> None:
    ws = AsyncMockWebSocket()
    ws.push_recv(RECONNECT)
    ws.push_recv(_tokens("one", 1))

    with patch("soniox.realtime.async_stt.async_ws_connect", return_value=ws):
        async with async_client.realtime.stt.connect(config=CONFIG) as session:
            await session.receive_event()  # Takes the token, so the stream can resume.
            await session._drop_socket()  # pyright: ignore[reportPrivateUsage]

            await session.send_byte_chunk(b"during")

            state = session._reconnect  # pyright: ignore[reportPrivateUsage]
            assert state is not None
            assert state.resend_after(0, "token-2") == [b"during"]


# ---------------------------------------------------------------------------
# Endings that arrive while a read is waiting
# ---------------------------------------------------------------------------


def test_closing_while_a_read_waits_is_the_end_of_the_events(client: SonioxClient) -> None:
    """The documented pattern: one thread reads, the owner closes.

    `close()` takes the socket away under the read. The read is bounded, so it
    comes back to a session with nothing to read from, and an ending is what
    the caller's loop expects there - not an attribute error about `None`.
    """
    silent = MockWebSocket()
    silent.push_recv(RECONNECT)
    silent.go_silent()

    with patch("soniox.realtime.stt.sync_ws_connect", side_effect=[silent, MockWebSocket()]):
        session = client.realtime.stt.connect(config=CONFIG)
        session._ping_interval_sec = 1.0  # pyright: ignore[reportPrivateUsage]
        session.enter()
        def close_once_the_read_is_waiting() -> None:
            time.sleep(0.2)
            session.close()

        closing = threading.Thread(target=close_once_the_read_is_waiting)
        closing.start()
        # Whatever the read raises when its socket is taken comes out here.
        assert session.receive_event() is None
        closing.join(5)


async def test_closing_while_a_read_waits_is_the_end_of_the_events_async(
    async_client: AsyncSonioxClient,
) -> None:
    silent = AsyncMockWebSocket()
    silent.push_recv(RECONNECT)
    silent.go_silent()

    with patch(
        "soniox.realtime.async_stt.async_ws_connect",
        side_effect=[silent, AsyncMockWebSocket()],
    ):
        session = async_client.realtime.stt.connect(config=CONFIG)
        session._ping_interval_sec = 1.0  # pyright: ignore[reportPrivateUsage]
        await session.aenter()

        async def close_once_the_read_is_waiting() -> None:
            await asyncio.sleep(0.2)
            await session.close()

        closing = asyncio.ensure_future(close_once_the_read_is_waiting())
        # Whatever the cancelled read raises comes out here.
        assert await session.receive_event() is None
        await closing


# ---------------------------------------------------------------------------
# Replies that are not `reconnected`
# ---------------------------------------------------------------------------


def test_a_reply_that_cannot_be_read_is_dialled_again(client: SonioxClient) -> None:
    """Something in the way answers with a page, not our protocol.

    That is the same cause as a 5xx handshake - the way in is broken, not the
    stream - so it gets the same answer: let the connection go and dial again
    while the window lasts.
    """
    dropped, babbling, resumed = MockWebSocket(), MockWebSocket(), MockWebSocket()
    dropped.push_recv(RECONNECT)
    dropped.push_recv_error(ConnectionClosed(None, None))
    babbling.push_recv_raw("<html><body>502 Bad Gateway</body></html>")
    resumed.push_recv({"type": "reconnected", "reconnect_token": "token-2", "last_request": 0})
    resumed.push_recv(_tokens("one", 1))
    resumed.push_recv({"finished": True})
    resumed.close_after_recv()

    with (
        patch("soniox.realtime.stt.sync_ws_connect", side_effect=[dropped, babbling, resumed]),
        patch("soniox.realtime.stt.time.sleep"),
    ):
        with client.realtime.stt.connect(config=CONFIG) as session:
            received = list(session.receive_events())

    assert [token.text for event in received for token in event.tokens] == ["one"]
    assert babbling.aborted, "the connection was left open"
    assert not babbling.ended_by_us, "a close with 1000 would have ended the stream"


async def test_a_reply_that_cannot_be_read_is_dialled_again_async(
    async_client: AsyncSonioxClient,
) -> None:
    dropped, babbling, resumed = (
        AsyncMockWebSocket(),
        AsyncMockWebSocket(),
        AsyncMockWebSocket(),
    )
    dropped.push_recv(RECONNECT)
    dropped.push_recv_error(ConnectionClosed(None, None))
    babbling.push_recv_raw("<html><body>502 Bad Gateway</body></html>")
    resumed.push_recv({"type": "reconnected", "reconnect_token": "token-2", "last_request": 0})
    resumed.push_recv(_tokens("one", 1))
    resumed.push_recv({"finished": True})
    resumed.close_after_recv()

    with (
        patch(
            "soniox.realtime.async_stt.async_ws_connect",
            side_effect=[dropped, babbling, resumed],
        ),
        patch("soniox.realtime.async_stt.asyncio.sleep"),
    ):
        async with async_client.realtime.stt.connect(config=CONFIG) as session:
            received = [event async for event in session.receive_events()]

    assert [token.text for event in received for token in event.tokens] == ["one"]
    assert babbling.aborted, "the connection was left open"


def test_a_stream_a_newer_connection_holds_is_not_dialled_again(
    client: SonioxClient,
) -> None:
    """`connection_replaced` is the one refusal that is not an ending.

    The stream runs on, on someone else's connection, so this one has nothing
    left to do and nothing to end: a close here could reach the server as the
    end of a stream still in use.
    """
    dropped, replaced = MockWebSocket(), MockWebSocket()
    dropped.push_recv(RECONNECT)
    dropped.push_recv_error(ConnectionClosed(None, None))
    replaced.push_recv(
        {
            "error_code": 400,
            "error_type": "connection_replaced",
            "error_message": "A newer connection has this stream.",
        }
    )

    with patch(
        "soniox.realtime.stt.sync_ws_connect", side_effect=[dropped, replaced]
    ) as connect:
        with client.realtime.stt.connect(config=CONFIG) as session:
            received = list(session.receive_events())
            assert session._over is Ending.TAKEN  # pyright: ignore[reportPrivateUsage]

    # The caller is told, which is what the same frame on a live connection does
    assert [event.error_type for event in received] == ["connection_replaced"]
    assert connect.call_count == 2, "it kept dialling for a stream it cannot have"
    assert not replaced.ended_by_us, "it ended a stream the newer connection holds"


async def test_a_stream_a_newer_connection_holds_is_not_dialled_again_async(
    async_client: AsyncSonioxClient,
) -> None:
    dropped, replaced = AsyncMockWebSocket(), AsyncMockWebSocket()
    dropped.push_recv(RECONNECT)
    dropped.push_recv_error(ConnectionClosed(None, None))
    replaced.push_recv(
        {
            "error_code": 400,
            "error_type": "connection_replaced",
            "error_message": "A newer connection has this stream.",
        }
    )

    with patch(
        "soniox.realtime.async_stt.async_ws_connect", side_effect=[dropped, replaced]
    ) as connect:
        async with async_client.realtime.stt.connect(config=CONFIG) as session:
            received = [event async for event in session.receive_events()]
            assert session._over is Ending.TAKEN  # pyright: ignore[reportPrivateUsage]

    assert [event.error_type for event in received] == ["connection_replaced"]
    assert connect.call_count == 2, "it kept dialling for a stream it cannot have"
    assert not replaced.ended_by_us, "it ended a stream the newer connection holds"


def test_a_reply_with_no_count_is_a_refusal(client: SonioxClient) -> None:
    """Without the count there is no telling what the server already has.

    Resending from the first message would transcribe that audio twice, and the
    server does not notice: it transcribes what it is sent. A refusal costs one
    stream; a wrong transcript is worse and silent.
    """
    dropped, countless = MockWebSocket(), MockWebSocket()
    dropped.push_recv(RECONNECT)
    dropped.push_recv_error(ConnectionClosed(None, None))
    countless.push_recv({"type": "reconnected", "reconnect_token": "token-2"})

    with patch("soniox.realtime.stt.sync_ws_connect", side_effect=[dropped, countless]):
        with client.realtime.stt.connect(config=CONFIG) as session:
            session.send_byte_chunk(b"first")
            with pytest.raises(SonioxRealtimeError, match="could not be continued"):
                list(session.receive_events())

    assert _heard(countless) == [], "audio was resent to a connection that refused"


def test_a_connection_that_dies_mid_resend_is_continued_again(client: SonioxClient) -> None:
    """A connection can accept, answer, and die before the resend lands.

    The resend log is untouched by a failed send, so the next read finds the
    dead socket and continues the stream again - which must be what the caller
    sees, not a raw websockets error.
    """

    class _DiesAfterReplying(MockWebSocket):
        def recv(self, timeout: float | None = None) -> str | bytes:
            message = super().recv(timeout)
            self.closed = True  # The resend lands on a socket already gone.
            return message

    dropped, dying, resumed = MockWebSocket(), _DiesAfterReplying(), MockWebSocket()
    dropped.push_recv(RECONNECT)
    dropped.push_recv_error(ConnectionClosed(None, None))
    dying.push_recv({"type": "reconnected", "reconnect_token": "token-2", "last_request": 0})
    resumed.push_recv({"type": "reconnected", "reconnect_token": "token-3", "last_request": 0})
    resumed.push_recv(_tokens("one", 1))
    resumed.push_recv({"finished": True})
    resumed.close_after_recv()

    with patch(
        "soniox.realtime.stt.sync_ws_connect", side_effect=[dropped, dying, resumed]
    ) as connect:
        with client.realtime.stt.connect(config=CONFIG) as session:
            session.send_byte_chunk(b"first")
            received = list(session.receive_events())

    assert connect.call_count == 3, "the stream was dropped when the resend failed"
    assert [token.text for event in received for token in event.tokens] == ["one"]
    # The audio the first connection never acknowledged is still owed, so it
    # goes to the connection that does take the stream over.
    assert _heard(resumed) == [b"first"]


def test_a_ping_never_lands_on_a_connection_that_is_still_dialling(
    client: SonioxClient,
) -> None:
    """The reconnect frame must be the first and only message on the socket.

    The server refuses a dial whose first message is anything else, and the
    keepalive is the one writer that runs without being asked. So this makes a
    real ping tick while the dial waits for its reply.
    """

    class _SlowReply(MockWebSocket):
        """A dial whose reply takes long enough for the keepalive to tick."""

        def __init__(self, reply: dict) -> None:
            super().__init__()
            self._reply: dict | None = reply
            self.heard_before_replying: list[Any] = []

        def recv(self, timeout: float | None = None) -> str | bytes:
            if self._reply is None:
                return super().recv(timeout)
            reply, self._reply = self._reply, None
            time.sleep(0.15)  # Long enough for the keepalive to tick.
            self.heard_before_replying = list(self.sent_messages)
            return json.dumps(reply)

    silent = MockWebSocket()
    silent.push_recv(RECONNECT)
    silent.go_silent()
    resumed = _SlowReply({"type": "reconnected", "reconnect_token": "token-2", "last_request": 0})
    resumed.push_recv({"finished": True})
    resumed.close_after_recv()

    # A keepalive fast enough to tick many times inside that reply, which is
    # also what makes the unanswered ping notice the silence.
    with (
        patch("soniox.realtime.stt.PING_INTERVAL_SEC", 0.01),
        patch("soniox.realtime.stt.sync_ws_connect", side_effect=[silent, resumed]),
    ):
        with client.realtime.stt.connect(config=CONFIG) as session:
            list(session.receive_events())

    assert resumed.heard_before_replying == [
        {"type": "reconnect", "reconnect_token": "token-1", "last_seq": 0}
    ], "something else reached the connection before the server answered"


# ---------------------------------------------------------------------------
# The async half of the retry path
# ---------------------------------------------------------------------------


async def test_a_dial_that_is_never_answered_is_let_go_async(
    async_client: AsyncSonioxClient,
) -> None:
    dropped = AsyncMockWebSocket()
    dropped.push_recv(RECONNECT)
    dropped.push_recv_error(ConnectionClosed(None, None))
    config = CONFIG.model_copy(update={"idle_timeout_ms": 4000})
    dials: list[AsyncMockWebSocket] = []

    def dial(*_args: Any, **_kwargs: Any) -> AsyncMockWebSocket:
        if not dials:
            dials.append(dropped)
            return dropped
        silent = AsyncMockWebSocket()
        silent.push_recv_error(TimeoutError())
        dials.append(silent)
        return silent

    with (
        patch("soniox.realtime.async_stt.async_ws_connect", side_effect=dial),
        patch("soniox.realtime.async_stt.asyncio.sleep"),
    ):
        async with async_client.realtime.stt.connect(config=config) as session:
            with pytest.raises(SonioxRealtimeError, match="window closed"):
                [event async for event in session.receive_events()]

    # Every connection is let go, and carried nothing but the request.
    assert dials[1:], "no dial was attempted"
    assert all(ws.aborted for ws in dials[1:]), "a connection was left open"
    for socket in dials[1:]:
        assert [m.get("type") for m in socket.sent_messages] == ["reconnect"]


async def test_a_stream_not_continued_before_its_window_closes_says_so_async(
    async_client: AsyncSonioxClient,
) -> None:
    """The window is one idle timeout, and the clock does not stop for us.

    Every attempt and every wait between them spends exactly what it was given,
    which is what a server that answers nothing at all does. No attempt may run
    past the window, so the last dial is the one the window has room for.
    """
    dropped = AsyncMockWebSocket()
    dropped.push_recv(RECONNECT)
    dropped.push_recv_error(ConnectionClosed(None, None))
    config = CONFIG.model_copy(update={"idle_timeout_ms": 4000})
    now = [0.0]
    timeouts: list[float] = []
    dials = 0

    def dial(*_args: Any, **kwargs: Any) -> AsyncMockWebSocket:
        nonlocal dials
        dials += 1
        if dials == 1:
            return dropped
        timeouts.append(kwargs["open_timeout"])
        now[0] += kwargs["open_timeout"]
        raise TimeoutError

    async def spend(sec: float) -> None:
        now[0] += sec

    with (
        patch("soniox.realtime.async_stt.async_ws_connect", side_effect=dial),
        patch("soniox.realtime.async_stt.asyncio.sleep", side_effect=spend),
        patch("soniox.realtime.async_stt.time.monotonic", side_effect=lambda: now[0]),
    ):
        async with async_client.realtime.stt.connect(config=config) as session:
            with pytest.raises(SonioxRealtimeError, match="window closed"):
                [event async for event in session.receive_events()]

    assert timeouts, "no dial was attempted"
    assert timeouts[0] <= 4.0 / 2, f"the first dial was given {timeouts[0]}s of a 4s window"
    assert now[0] <= 4.0, f"the dials ran {now[0]}s past a 4s window"


async def test_a_session_closed_while_it_dials_lets_the_new_connection_go_async(
    async_client: AsyncSonioxClient,
) -> None:
    """A stream nobody ends waits out its idle timeout, billed on wall clock.

    So the connection that answered is closed rather than abandoned: the close
    is what tells the server the stream is over.
    """
    dropped, resumed = AsyncMockWebSocket(), AsyncMockWebSocket()
    dropped.push_recv(RECONNECT)
    dropped.push_recv(_tokens("one", 1))
    dropped.push_recv_error(ConnectionClosed(None, None))
    resumed.push_recv({"type": "reconnected", "reconnect_token": "token-2", "last_request": 0})

    session = async_client.realtime.stt.connect(config=CONFIG)
    dialled: list[AsyncMockWebSocket] = []

    def dial(*_args: object, **_kwargs: object) -> AsyncMockWebSocket:
        dialled.append(AsyncMockWebSocket())
        if len(dialled) == 1:
            return dropped
        if len(dialled) == 2:
            # The caller is done while the reconnect is in flight. Closing from
            # here is what the race looks like from the dial's point of view.
            session._over = Ending.CLOSING  # pyright: ignore[reportPrivateUsage]
            return resumed
        return dialled[-1]

    with patch("soniox.realtime.async_stt.async_ws_connect", side_effect=dial):
        async with session:
            received = [event async for event in session.receive_events()]

    assert [token.text for event in received for token in event.tokens] == ["one"]
    # This connection has the stream, so closing it is what ends the stream.
    # Letting it go would leave the stream waiting out its idle timeout.
    assert resumed.ended_by_us >= 1, "the stream was left running on a closed session"


async def test_a_pong_confirms_the_messages_the_server_has_async(
    async_client: AsyncSonioxClient,
) -> None:
    """The pong is what trims the resend log, and it arrives on the read path.

    Without it the log keeps every chunk of the stream, and a reconnect resends
    audio the server already has.
    """
    ws = AsyncMockWebSocket()
    ws.push_recv(RECONNECT)
    ws.push_recv(_tokens("one", 1))

    with patch("soniox.realtime.async_stt.async_ws_connect", return_value=ws):
        async with async_client.realtime.stt.connect(config=CONFIG) as session:
            state = session._reconnect  # pyright: ignore[reportPrivateUsage]
            assert state is not None
            # The token comes with the first read, and the wait for a pong
            # starts there rather than at the start request.
            await session.receive_event()

            await session.send_byte_chunk(b"first")
            ping = state.ping()
            await session.send_byte_chunk(b"second")
            ws.push_recv({"type": "pong", "id": int(ping.split('"id": ')[1].rstrip("}"))})
            ws.push_recv(_tokens("two", 2))

            # The pong is the protocol's own, so this read returns the tokens
            # behind it - and recording the pong is what trims the log.
            event = await session.receive_event()

    assert event is not None and [t.text for t in event.tokens] == ["two"]
    # "first" was confirmed by the pong; "second" was still in flight.
    assert state.resend_after(0, "token-2") == [b"second"]



def test_a_stream_that_never_answers_is_not_continued_for_ever(
    client: SonioxClient,
) -> None:
    """A connection can answer `reconnected` and die before the resend lands.

    Every success hands back a new token and starts the window again, so the
    bookkeeping alone has nothing left to stop on, so this is where the client
    draws its own line.
    """

    class _AnswersThenDies(MockWebSocket):
        def recv(self, timeout: float | None = None) -> str | bytes:
            message = super().recv(timeout)
            self.closed = True  # Gone before the resend lands.
            return message

    dials: list[MockWebSocket] = []

    def dial(*_args: Any, **_kwargs: Any) -> MockWebSocket:
        if not dials:
            first = MockWebSocket()
            first.push_recv(RECONNECT)
            first.push_recv_error(ConnectionClosed(None, None))
            dials.append(first)
            return first
        dying = _AnswersThenDies()
        dying.push_recv(
            {"type": "reconnected", "reconnect_token": f"token-{len(dials)}", "last_request": 0}
        )
        dials.append(dying)
        return dying

    with (
        patch("soniox.realtime.stt.sync_ws_connect", side_effect=dial),
        patch("soniox.realtime.stt.time.sleep"),
    ):
        with client.realtime.stt.connect(config=CONFIG) as session:
            session.send_byte_chunk(b"first")
            with pytest.raises(SonioxRealtimeError, match="no response from the server"):
                list(session.receive_events())

    assert len(dials) == 1 + MAX_RESUMES_WITHOUT_A_FRAME


def test_a_working_stream_is_continued_as_often_as_it_drops(client: SonioxClient) -> None:
    """The cap counts takeovers in a row that got nothing back, not takeovers.

    A long session on a flaky network drops far more than ten times, and each
    of those drops has a response behind it, so none of them is near the cap.
    """
    drops = MAX_RESUMES_WITHOUT_A_FRAME + 2
    sockets: list[MockWebSocket] = []
    for n in range(drops + 1):
        ws = MockWebSocket()
        if n == 0:
            ws.push_recv(RECONNECT)
        else:
            ws.push_recv(
                {"type": "reconnected", "reconnect_token": f"token-{n + 1}", "last_request": 0}
            )
        # The response that proves this takeover reached a live stream.
        ws.push_recv(_tokens(f"word{n}", n + 1))
        if n == drops:
            ws.push_recv({"finished": True})
            ws.close_after_recv()
        else:
            ws.push_recv_error(ConnectionClosed(None, None))
        sockets.append(ws)

    with (
        patch("soniox.realtime.stt.sync_ws_connect", side_effect=sockets),
        patch("soniox.realtime.stt.time.sleep"),
    ):
        with client.realtime.stt.connect(config=CONFIG) as session:
            received = list(session.receive_events())

    assert [token.text for event in received for token in event.tokens] == [
        f"word{n}" for n in range(drops + 1)
    ]


def test_reading_a_stream_that_is_over_is_the_end_of_the_events(
    client: SonioxClient,
) -> None:
    """Reading on past the end is how a caller's loop ends, not a misuse."""
    ws = MockWebSocket()
    ws.push_recv(RECONNECT)
    ws.push_recv({"finished": True})
    ws.close_after_recv()

    with patch("soniox.realtime.stt.sync_ws_connect", return_value=ws):
        with client.realtime.stt.connect(config=CONFIG) as session:
            assert list(session.receive_events())  # Up to and including the end.
            assert session.receive_event() is None
            assert session.receive_event() is None


async def test_a_reply_with_no_count_is_a_refusal_async(
    async_client: AsyncSonioxClient,
) -> None:
    dropped, countless = AsyncMockWebSocket(), AsyncMockWebSocket()
    dropped.push_recv(RECONNECT)
    dropped.push_recv_error(ConnectionClosed(None, None))
    countless.push_recv({"type": "reconnected", "reconnect_token": "token-2"})

    with patch(
        "soniox.realtime.async_stt.async_ws_connect", side_effect=[dropped, countless]
    ):
        async with async_client.realtime.stt.connect(config=CONFIG) as session:
            await session.send_byte_chunk(b"first")
            with pytest.raises(SonioxRealtimeError, match="could not be continued"):
                [event async for event in session.receive_events()]

    assert _heard(countless) == [], "audio was resent to a connection that refused"


async def test_a_connection_that_dies_mid_resend_is_continued_again_async(
    async_client: AsyncSonioxClient,
) -> None:
    class _DiesAfterReplying(AsyncMockWebSocket):
        async def recv(self, timeout: float | None = None) -> str | bytes:
            message = await super().recv(timeout)
            self.closed = True  # The resend lands on a socket already gone.
            return message

    dropped, dying, resumed = (
        AsyncMockWebSocket(),
        _DiesAfterReplying(),
        AsyncMockWebSocket(),
    )
    dropped.push_recv(RECONNECT)
    dropped.push_recv_error(ConnectionClosed(None, None))
    dying.push_recv({"type": "reconnected", "reconnect_token": "token-2", "last_request": 0})
    resumed.push_recv({"type": "reconnected", "reconnect_token": "token-3", "last_request": 0})
    resumed.push_recv(_tokens("one", 1))
    resumed.push_recv({"finished": True})
    resumed.close_after_recv()

    with patch(
        "soniox.realtime.async_stt.async_ws_connect", side_effect=[dropped, dying, resumed]
    ) as connect:
        async with async_client.realtime.stt.connect(config=CONFIG) as session:
            await session.send_byte_chunk(b"first")
            received = [event async for event in session.receive_events()]

    assert connect.call_count == 3, "the stream was dropped when the resend failed"
    assert [token.text for event in received for token in event.tokens] == ["one"]
    assert _heard(resumed) == [b"first"]


async def test_a_stream_that_never_answers_is_not_continued_for_ever_async(
    async_client: AsyncSonioxClient,
) -> None:
    class _AnswersThenDies(AsyncMockWebSocket):
        async def recv(self, timeout: float | None = None) -> str | bytes:
            message = await super().recv(timeout)
            self.closed = True  # Gone before the resend lands.
            return message

    dials: list[AsyncMockWebSocket] = []

    def dial(*_args: Any, **_kwargs: Any) -> AsyncMockWebSocket:
        if not dials:
            first = AsyncMockWebSocket()
            first.push_recv(RECONNECT)
            first.push_recv_error(ConnectionClosed(None, None))
            dials.append(first)
            return first
        dying = _AnswersThenDies()
        dying.push_recv(
            {"type": "reconnected", "reconnect_token": f"token-{len(dials)}", "last_request": 0}
        )
        dials.append(dying)
        return dying

    with (
        patch("soniox.realtime.async_stt.async_ws_connect", side_effect=dial),
        patch("soniox.realtime.async_stt.asyncio.sleep"),
    ):
        async with async_client.realtime.stt.connect(config=CONFIG) as session:
            await session.send_byte_chunk(b"first")
            with pytest.raises(SonioxRealtimeError, match="no response from the server"):
                [event async for event in session.receive_events()]

    assert len(dials) == 1 + MAX_RESUMES_WITHOUT_A_FRAME


async def test_a_working_stream_is_continued_as_often_as_it_drops_async(
    async_client: AsyncSonioxClient,
) -> None:
    drops = MAX_RESUMES_WITHOUT_A_FRAME + 2
    sockets: list[AsyncMockWebSocket] = []
    for n in range(drops + 1):
        ws = AsyncMockWebSocket()
        if n == 0:
            ws.push_recv(RECONNECT)
        else:
            ws.push_recv(
                {"type": "reconnected", "reconnect_token": f"token-{n + 1}", "last_request": 0}
            )
        # The response that proves this takeover reached a live stream.
        ws.push_recv(_tokens(f"word{n}", n + 1))
        if n == drops:
            ws.push_recv({"finished": True})
            ws.close_after_recv()
        else:
            ws.push_recv_error(ConnectionClosed(None, None))
        sockets.append(ws)

    with (
        patch("soniox.realtime.async_stt.async_ws_connect", side_effect=sockets),
        patch("soniox.realtime.async_stt.asyncio.sleep"),
    ):
        async with async_client.realtime.stt.connect(config=CONFIG) as session:
            received = [event async for event in session.receive_events()]

    assert [token.text for event in received for token in event.tokens] == [
        f"word{n}" for n in range(drops + 1)
    ]


def test_a_ping_sent_before_the_stream_starts_does_not_end_it(
    client: SonioxClient,
) -> None:
    """A ping right after the start request is answered only once the stream is.

    So an unanswered one says nothing about the connection yet, and counting it
    kills streams the server is simply slow to open - including every stream
    the server declines to offer a reconnect for, which it may do for any
    stream.
    """
    slow = MockWebSocket()
    slow.go_silent()  # Nothing at all for now, not even the token.
    slow.push_recv(_tokens("one", 1))
    slow.push_recv({"finished": True})
    slow.close_after_recv()

    with patch("soniox.realtime.stt.sync_ws_connect", return_value=slow):
        with client.realtime.stt.connect(config=CONFIG) as session:
            session._ping_interval_sec = 0.01  # pyright: ignore[reportPrivateUsage]
            state = session._reconnect  # pyright: ignore[reportPrivateUsage]
            assert state is not None
            state.ping()  # Unanswered, and already older than the interval.
            time.sleep(0.05)

            # The silence runs out and the stream opens, which it would not
            # have had the unanswered ping been taken for a lost connection.
            assert not state.pong_overdue(0.0)
            received = list(session.receive_events())

    assert [token.text for event in received for token in event.tokens] == ["one"]


def test_a_lost_connection_that_cannot_be_continued_says_so(
    client: SonioxClient,
) -> None:
    """Silence is not an ending.

    A stream with no reconnect offered, whose pings stop being answered, is a
    lost connection rather than a transcript that
    finished. Ending the caller's loop would read as the latter.
    """
    silent = MockWebSocket()
    silent.push_recv(_tokens("one", 1))  # The stream starts, so pings count.
    silent.go_silent()

    with patch("soniox.realtime.stt.sync_ws_connect", return_value=silent):
        with client.realtime.stt.connect(config=CONFIG) as session:
            session._ping_interval_sec = 0.01  # pyright: ignore[reportPrivateUsage]
            with pytest.raises(SonioxRealtimeError, match="ping went unanswered"):
                list(session.receive_events())


async def test_a_lost_connection_that_cannot_be_continued_says_so_async(
    async_client: AsyncSonioxClient,
) -> None:
    silent = AsyncMockWebSocket()
    silent.push_recv(_tokens("one", 1))
    silent.go_silent()

    with patch("soniox.realtime.async_stt.async_ws_connect", return_value=silent):
        async with async_client.realtime.stt.connect(config=CONFIG) as session:
            session._ping_interval_sec = 0.01  # pyright: ignore[reportPrivateUsage]
            with pytest.raises(SonioxRealtimeError, match="ping went unanswered"):
                [event async for event in session.receive_events()]


def test_the_reconnect_token_is_not_handed_to_the_caller(client: SonioxClient) -> None:
    """The token is ours to present, and it is a credential for this stream.

    What a caller wants from the `reconnected` frame is that the stream dropped
    and came back, which the event's type already says.
    """
    dropped, resumed = MockWebSocket(), MockWebSocket()
    dropped.push_recv(RECONNECT)
    dropped.push_recv_error(ConnectionClosed(None, None))
    resumed.push_recv({"type": "reconnected", "reconnect_token": "token-2", "last_request": 0})
    resumed.push_recv({"finished": True})
    resumed.close_after_recv()

    with patch("soniox.realtime.stt.sync_ws_connect", side_effect=[dropped, resumed]):
        with client.realtime.stt.connect(config=CONFIG) as session:
            received = list(session.receive_events())

    reconnected = [event for event in received if event.type == "reconnected"]
    assert len(reconnected) == 1, "the caller was not told the stream dropped"
    assert reconnected[0].reconnect_token is None
    assert reconnected[0].last_request == 0, "the server's count is not a secret"

    # Stripping it from the caller's copy must not cost the session its own.
    state = session._reconnect  # pyright: ignore[reportPrivateUsage]
    assert state is not None
    assert state.token == "token-2"
