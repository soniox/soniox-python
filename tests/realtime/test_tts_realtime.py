"""
Realtime Text-to-Speech tests (sync) against a scripted mock WebSocket.

Covers the single-stream :class:`RealtimeTTSConnection` and the multiplexed
:class:`RealtimeTTSMultiplexedConnection` / :class:`RealtimeTTSStream`
surfaces - wire contract on send, routing on receive, error paths, and the
pause/resume + cancel control flows.
"""

from __future__ import annotations

import base64
from unittest.mock import patch

import pytest

from soniox.client import SonioxClient
from soniox.errors import SonioxRealtimeError
from soniox.realtime._constants import MAX_TTS_STREAMS_PER_CONNECTION
from soniox.types.realtime import RealtimeTTSConfig

from .mock_ws import MockWebSocket

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_AUDIO_BYTES = b"hello-pcm-bytes"
_AUDIO_B64 = base64.b64encode(_AUDIO_BYTES).decode()


def _config(stream_id: str = "s1") -> RealtimeTTSConfig:
    return RealtimeTTSConfig(
        stream_id=stream_id,
        model="m",
        language="en",
        voice="Adrian",
        audio_format="wav",
    )


def _patch_sync_tts_ws(ws: MockWebSocket):
    return patch("soniox.realtime.tts.sync_ws_connect", return_value=ws)


# ---------------------------------------------------------------------------
# Single-stream connection: wire contract on enter
# ---------------------------------------------------------------------------


def test_connect_sends_config_on_enter(client: SonioxClient) -> None:
    ws = MockWebSocket()
    ws.close_after_recv()

    with _patch_sync_tts_ws(ws):
        with client.realtime.tts.connect(config=_config()) as _:
            pass

    # First message is the config payload.
    config_msg = ws.sent_messages[0]
    assert config_msg["stream_id"] == "s1"
    assert config_msg["model"] == "m"
    assert config_msg["voice"] == "Adrian"
    assert config_msg["api_key"] == "test_key"


def test_connect_raises_realtime_error_on_ws_failure(client: SonioxClient) -> None:
    """Failures in the underlying ws connect surface as SonioxRealtimeError."""
    with patch(
        "soniox.realtime.tts.sync_ws_connect", side_effect=ConnectionError("boom")
    ):
        with pytest.raises(SonioxRealtimeError, match="Failed to start"):
            with client.realtime.tts.connect(config=_config()):
                pass


# ---------------------------------------------------------------------------
# Single-stream connection: send paths
# ---------------------------------------------------------------------------


def test_send_text_chunk_emits_payload(client: SonioxClient) -> None:
    ws = MockWebSocket()
    ws.close_after_recv()

    with _patch_sync_tts_ws(ws):
        with client.realtime.tts.connect(config=_config()) as conn:
            conn.send_text_chunk("hello", text_end=False)

    text_msgs = [m for m in ws.sent_messages if isinstance(m, dict) and m.get("text") == "hello"]
    assert len(text_msgs) == 1
    assert text_msgs[0]["stream_id"] == "s1"
    assert text_msgs[0]["text_end"] is False


def test_send_text_chunks_string_sends_one_message(client: SonioxClient) -> None:
    ws = MockWebSocket()
    ws.close_after_recv()

    with _patch_sync_tts_ws(ws):
        with client.realtime.tts.connect(config=_config()) as conn:
            conn.send_text_chunks("done", text_end=True)

    text_payloads = [m for m in ws.sent_messages if isinstance(m, dict) and "text" in m]
    assert text_payloads == [{"text": "done", "text_end": True, "stream_id": "s1"}]


def test_send_text_chunks_iterator_sends_each_then_finish(client: SonioxClient) -> None:
    ws = MockWebSocket()
    ws.close_after_recv()

    with _patch_sync_tts_ws(ws):
        with client.realtime.tts.connect(config=_config()) as conn:
            conn.send_text_chunks(iter(["a", "b", "c"]))  # default text_end=True

    text_payloads = [m for m in ws.sent_messages if isinstance(m, dict) and "text" in m]
    # Three chunks (text_end=False) + a final finish (text="" + text_end=True).
    assert [p["text"] for p in text_payloads] == ["a", "b", "c", ""]
    assert [p["text_end"] for p in text_payloads] == [False, False, False, True]


def test_send_text_chunks_iterator_without_text_end(client: SonioxClient) -> None:
    ws = MockWebSocket()
    ws.close_after_recv()

    with _patch_sync_tts_ws(ws):
        with client.realtime.tts.connect(config=_config()) as conn:
            conn.send_text_chunks(iter(["a", "b"]), text_end=False)

    text_payloads = [m for m in ws.sent_messages if isinstance(m, dict) and "text" in m]
    assert [p["text"] for p in text_payloads] == ["a", "b"]
    assert all(not p["text_end"] for p in text_payloads)


def test_finish_sends_empty_text_with_text_end(client: SonioxClient) -> None:
    ws = MockWebSocket()
    ws.close_after_recv()

    with _patch_sync_tts_ws(ws):
        with client.realtime.tts.connect(config=_config()) as conn:
            conn.finish()

    finish_msgs = [
        m for m in ws.sent_messages
        if isinstance(m, dict) and m.get("text_end") is True and m.get("text") == ""
    ]
    assert len(finish_msgs) == 1


def test_cancel_sends_cancel_payload(client: SonioxClient) -> None:
    ws = MockWebSocket()
    ws.close_after_recv()

    with _patch_sync_tts_ws(ws):
        with client.realtime.tts.connect(config=_config()) as conn:
            conn.cancel()

    cancel_msgs = [m for m in ws.sent_messages if isinstance(m, dict) and m.get("cancel")]
    assert cancel_msgs == [{"stream_id": "s1", "cancel": True}]


def test_keep_alive_sends_keepalive_payload(client: SonioxClient) -> None:
    ws = MockWebSocket()
    ws.close_after_recv()

    with _patch_sync_tts_ws(ws):
        with client.realtime.tts.connect(config=_config()) as conn:
            conn.keep_alive()

    assert {"keep_alive": True} in ws.sent_messages


@pytest.mark.parametrize(
    "method, args",
    [
        ("send_text_chunk", ("hi",)),
        ("cancel", ()),
        ("keep_alive", ()),
        ("pause", ()),
        ("resume", ()),
        ("recv_bytes", ()),
        ("receive_event", ()),
    ],
)
def test_method_raises_when_not_connected(
    client: SonioxClient, method: str, args: tuple
) -> None:
    conn = client.realtime.tts.connect(config=_config())
    with pytest.raises(SonioxRealtimeError, match="not connected"):
        getattr(conn, method)(*args)


def test_send_text_chunk_wraps_send_errors(client: SonioxClient) -> None:
    ws = MockWebSocket()
    ws.close_after_recv()

    with _patch_sync_tts_ws(ws):
        with client.realtime.tts.connect(config=_config()) as conn:
            ws.closed = True  # next .send raises ConnectionClosed
            with pytest.raises(SonioxRealtimeError, match="Failed to send text chunk"):
                conn.send_text_chunk("hi")


def test_cancel_wraps_send_errors(client: SonioxClient) -> None:
    ws = MockWebSocket()
    ws.close_after_recv()

    with _patch_sync_tts_ws(ws):
        with client.realtime.tts.connect(config=_config()) as conn:
            ws.closed = True
            with pytest.raises(SonioxRealtimeError, match="Failed to cancel"):
                conn.cancel()


def test_keep_alive_wraps_send_errors(client: SonioxClient) -> None:
    ws = MockWebSocket()
    ws.close_after_recv()

    with _patch_sync_tts_ws(ws):
        with client.realtime.tts.connect(config=_config()) as conn:
            ws.closed = True
            with pytest.raises(SonioxRealtimeError, match="Failed to send keep-alive"):
                conn.keep_alive()


# ---------------------------------------------------------------------------
# Single-stream connection: pause / resume
# ---------------------------------------------------------------------------


def test_pause_suspends_sending_and_starts_keepalive(client: SonioxClient) -> None:
    ws = MockWebSocket()
    ws.close_after_recv()

    with _patch_sync_tts_ws(ws):
        with client.realtime.tts.connect(config=_config()) as conn:
            conn.send_text_chunk("before", text_end=False)
            conn.pause()
            assert conn.paused is True
            conn.send_text_chunk("during", text_end=False)  # dropped
            conn.resume()
            assert conn.paused is False
            conn.send_text_chunk("after", text_end=False)

    sent_texts = [
        m["text"] for m in ws.sent_messages
        if isinstance(m, dict) and "text" in m
    ]
    assert sent_texts == ["before", "after"]


def test_pause_is_idempotent(client: SonioxClient) -> None:
    ws = MockWebSocket()
    ws.close_after_recv()

    with _patch_sync_tts_ws(ws):
        with client.realtime.tts.connect(config=_config()) as conn:
            conn.pause()
            conn.pause()  # no error
            assert conn.paused is True


def test_resume_when_not_paused_is_noop(client: SonioxClient) -> None:
    ws = MockWebSocket()
    ws.close_after_recv()

    with _patch_sync_tts_ws(ws):
        with client.realtime.tts.connect(config=_config()) as conn:
            conn.resume()  # not paused - must not raise
            assert conn.paused is False


# ---------------------------------------------------------------------------
# Single-stream connection: receive paths
# ---------------------------------------------------------------------------


def test_receive_event_returns_audio(client: SonioxClient) -> None:
    ws = MockWebSocket()
    ws.push_recv({"audio": _AUDIO_B64})
    ws.close_after_recv()

    with _patch_sync_tts_ws(ws):
        with client.realtime.tts.connect(config=_config()) as conn:
            event = conn.receive_event()

    assert event is not None
    assert event.audio == _AUDIO_B64
    assert event.audio_bytes() == _AUDIO_BYTES


def test_receive_event_returns_none_on_connection_close(client: SonioxClient) -> None:
    ws = MockWebSocket()
    ws.close_after_recv()

    with _patch_sync_tts_ws(ws):
        with client.realtime.tts.connect(config=_config()) as conn:
            event = conn.receive_event()

    assert event is None


def test_receive_event_raises_on_error_event(client: SonioxClient) -> None:
    ws = MockWebSocket()
    ws.push_recv({"error_code": 500, "error_message": "boom"})
    ws.close_after_recv()

    with _patch_sync_tts_ws(ws):
        with client.realtime.tts.connect(config=_config()) as conn:
            with pytest.raises(SonioxRealtimeError, match="boom"):
                conn.receive_event()


def test_receive_event_raises_on_error_event_without_message(client: SonioxClient) -> None:
    """Default error message is used when none is provided."""
    ws = MockWebSocket()
    ws.push_recv({"error_code": 500})
    ws.close_after_recv()

    with _patch_sync_tts_ws(ws):
        with client.realtime.tts.connect(config=_config()) as conn:
            with pytest.raises(SonioxRealtimeError, match="code 500"):
                conn.receive_event()


def test_receive_events_stops_on_terminated(client: SonioxClient) -> None:
    ws = MockWebSocket()
    ws.push_recv({"audio": _AUDIO_B64})
    ws.push_recv({"audio_end": True})
    ws.push_recv({"terminated": True})
    ws.push_recv({"audio": _AUDIO_B64})  # should not be reached
    ws.close_after_recv()

    with _patch_sync_tts_ws(ws):
        with client.realtime.tts.connect(config=_config()) as conn:
            events = list(conn.receive_events())

    assert len(events) == 3
    assert events[-1].terminated is True


def test_receive_audio_chunks_yields_decoded_bytes(client: SonioxClient) -> None:
    ws = MockWebSocket()
    ws.push_recv({"audio": _AUDIO_B64})
    ws.push_recv({"audio": _AUDIO_B64, "terminated": True})
    ws.close_after_recv()

    with _patch_sync_tts_ws(ws):
        with client.realtime.tts.connect(config=_config()) as conn:
            chunks = list(conn.receive_audio_chunks())

    assert chunks == [_AUDIO_BYTES, _AUDIO_BYTES]


def test_receive_audio_chunks_raises_on_invalid_base64(client: SonioxClient) -> None:
    ws = MockWebSocket()
    ws.push_recv({"audio": "not-base64!@#"})
    ws.close_after_recv()

    with _patch_sync_tts_ws(ws):
        with client.realtime.tts.connect(config=_config()) as conn:
            with pytest.raises(SonioxRealtimeError, match="Invalid"):
                list(conn.receive_audio_chunks())


def test_last_message_tracks_most_recent_event(client: SonioxClient) -> None:
    ws = MockWebSocket()
    ws.push_recv({"audio": _AUDIO_B64})
    ws.push_recv({"terminated": True})
    ws.close_after_recv()

    with _patch_sync_tts_ws(ws):
        with client.realtime.tts.connect(config=_config()) as conn:
            assert conn.last_message is None
            list(conn.receive_events())
            assert conn.last_message is not None
            assert conn.last_message.terminated is True


def test_receive_event_raises_on_recv_timeout(client: SonioxClient) -> None:
    ws = MockWebSocket()
    ws.push_recv_error(TimeoutError("slow"))

    with _patch_sync_tts_ws(ws):
        with client.realtime.tts.connect(config=_config()) as conn:
            with pytest.raises(SonioxRealtimeError, match="Timed out"):
                conn.receive_event()


def test_close_idempotent_after_exit(client: SonioxClient) -> None:
    ws = MockWebSocket()
    ws.close_after_recv()

    with _patch_sync_tts_ws(ws):
        with client.realtime.tts.connect(config=_config()) as conn:
            pass
        # exit already closed; explicit close must be a no-op.
        conn.close()


def test_close_before_enter_is_noop(client: SonioxClient) -> None:
    conn = client.realtime.tts.connect(config=_config())
    conn.close()  # must not raise


# ---------------------------------------------------------------------------
# Multiplexed connection
# ---------------------------------------------------------------------------


def test_multiplexed_connect_does_not_send_until_open_stream(client: SonioxClient) -> None:
    ws = MockWebSocket()
    ws.close_after_recv()

    with _patch_sync_tts_ws(ws):
        with client.realtime.tts.connect_multi_stream() as _:
            pass

    assert ws.sent_messages == []


def test_multiplexed_connect_wraps_ws_failure(client: SonioxClient) -> None:
    with patch(
        "soniox.realtime.tts.sync_ws_connect", side_effect=ConnectionError("nope")
    ):
        with pytest.raises(SonioxRealtimeError, match="Failed to start"):
            with client.realtime.tts.connect_multi_stream():
                pass


def test_open_stream_sends_config(client: SonioxClient) -> None:
    ws = MockWebSocket()
    ws.close_after_recv()

    with _patch_sync_tts_ws(ws):
        with client.realtime.tts.connect_multi_stream() as conn:
            conn.open_stream(config=_config("alpha"))

    config_msgs = [
        m for m in ws.sent_messages
        if isinstance(m, dict) and m.get("stream_id") == "alpha" and "model" in m
    ]
    assert len(config_msgs) == 1


def test_open_stream_rejects_duplicate_stream_id(client: SonioxClient) -> None:
    ws = MockWebSocket()
    ws.close_after_recv()

    with _patch_sync_tts_ws(ws):
        with client.realtime.tts.connect_multi_stream() as conn:
            conn.open_stream(config=_config("alpha"))
            with pytest.raises(SonioxRealtimeError, match="already active"):
                conn.open_stream(config=_config("alpha"))


def test_open_stream_rejects_when_at_limit(client: SonioxClient) -> None:
    ws = MockWebSocket()
    ws.close_after_recv()

    with _patch_sync_tts_ws(ws):
        with client.realtime.tts.connect_multi_stream() as conn:
            for i in range(MAX_TTS_STREAMS_PER_CONNECTION):
                conn.open_stream(config=_config(f"s{i}"))
            with pytest.raises(SonioxRealtimeError, match="Maximum"):
                conn.open_stream(config=_config("overflow"))


def test_open_stream_raises_when_not_connected(client: SonioxClient) -> None:
    conn = client.realtime.tts.connect_multi_stream()
    with pytest.raises(SonioxRealtimeError, match="not connected"):
        conn.open_stream(config=_config())


def test_multiplexed_routes_events_by_stream_id(client: SonioxClient) -> None:
    """Events arriving on the shared ws are routed to the matching stream's queue."""
    ws = MockWebSocket()
    ws.push_recv({"stream_id": "a", "audio": _AUDIO_B64})
    ws.push_recv({"stream_id": "b", "audio": _AUDIO_B64})
    ws.push_recv({"stream_id": "a", "terminated": True})
    ws.push_recv({"stream_id": "b", "terminated": True})
    ws.close_after_recv()

    with _patch_sync_tts_ws(ws):
        with client.realtime.tts.connect_multi_stream() as conn:
            stream_a = conn.open_stream(config=_config("a"))
            stream_b = conn.open_stream(config=_config("b"))
            events_a = list(stream_a.receive_events())
            events_b = list(stream_b.receive_events())

    assert {e.stream_id for e in events_a} == {"a"}
    assert {e.stream_id for e in events_b} == {"b"}
    assert events_a[-1].terminated and events_b[-1].terminated


def test_multiplexed_stream_send_methods_emit_correctly(client: SonioxClient) -> None:
    ws = MockWebSocket()
    ws.close_after_recv()

    with _patch_sync_tts_ws(ws):
        with client.realtime.tts.connect_multi_stream() as conn:
            stream = conn.open_stream(config=_config("zeta"))
            stream.send_text_chunk("hi")
            stream.send_text_chunks("done", text_end=True)
            stream.send_text_chunks(iter(["x", "y"]))
            stream.cancel()
            stream.keep_alive()

    text_msgs = [m for m in ws.sent_messages if isinstance(m, dict) and "text" in m]
    cancel_msgs = [m for m in ws.sent_messages if isinstance(m, dict) and m.get("cancel")]
    assert all(m["stream_id"] == "zeta" for m in text_msgs)
    assert {"text": "hi", "text_end": False, "stream_id": "zeta"} in text_msgs
    assert {"text": "done", "text_end": True, "stream_id": "zeta"} in text_msgs
    assert cancel_msgs == [{"stream_id": "zeta", "cancel": True}]
    assert {"keep_alive": True} in ws.sent_messages


def test_multiplexed_stream_pause_drops_text_chunks(client: SonioxClient) -> None:
    ws = MockWebSocket()
    ws.close_after_recv()

    with _patch_sync_tts_ws(ws):
        with client.realtime.tts.connect_multi_stream() as conn:
            stream = conn.open_stream(config=_config("p"))
            stream.send_text_chunk("before")
            stream.pause()
            stream.send_text_chunk("during")  # dropped
            stream.resume()
            stream.send_text_chunk("after")

    sent_texts = [
        m["text"] for m in ws.sent_messages
        if isinstance(m, dict) and "text" in m
    ]
    assert sent_texts == ["before", "after"]


def test_multiplexed_pause_idempotent_resume_noop(client: SonioxClient) -> None:
    ws = MockWebSocket()
    ws.close_after_recv()

    with _patch_sync_tts_ws(ws):
        with client.realtime.tts.connect_multi_stream() as conn:
            conn.resume()  # not paused - no-op
            conn.pause()
            conn.pause()  # idempotent
            assert conn.paused is True


@pytest.mark.parametrize("method", ["pause", "resume"])
def test_multiplexed_method_raises_when_not_connected(
    client: SonioxClient, method: str
) -> None:
    conn = client.realtime.tts.connect_multi_stream()
    with pytest.raises(SonioxRealtimeError, match="not connected"):
        getattr(conn, method)()


def test_multiplexed_send_after_close_raises(client: SonioxClient) -> None:
    ws = MockWebSocket()
    ws.close_after_recv()

    with _patch_sync_tts_ws(ws):
        with client.realtime.tts.connect_multi_stream() as conn:
            stream = conn.open_stream(config=_config("x"))
        # Connection now closed - sending text chunk via stream raises.
        with pytest.raises(SonioxRealtimeError, match="not connected"):
            stream.send_text_chunk("after-close")


def test_multiplexed_global_error_event_raises_to_caller(client: SonioxClient) -> None:
    """Errors without a stream_id surface to the receiving stream."""
    ws = MockWebSocket()
    ws.push_recv({"error_code": 500, "error_message": "global"})
    ws.close_after_recv()

    with _patch_sync_tts_ws(ws):
        with client.realtime.tts.connect_multi_stream() as conn:
            stream = conn.open_stream(config=_config("only"))
            with pytest.raises(SonioxRealtimeError, match="global"):
                stream.receive_event()


def test_multiplexed_per_stream_error_deactivates_stream(client: SonioxClient) -> None:
    ws = MockWebSocket()
    ws.push_recv({"stream_id": "boom", "error_code": 42, "error_message": "fail"})
    ws.close_after_recv()

    with _patch_sync_tts_ws(ws):
        with client.realtime.tts.connect_multi_stream() as conn:
            stream = conn.open_stream(config=_config("boom"))
            with pytest.raises(SonioxRealtimeError, match="fail"):
                stream.receive_event()
            # Stream is deactivated → can re-open the same id.
            conn.open_stream(config=_config("boom"))


def test_multiplexed_terminated_event_deactivates_stream(client: SonioxClient) -> None:
    ws = MockWebSocket()
    ws.push_recv({"stream_id": "done", "terminated": True})
    ws.close_after_recv()

    with _patch_sync_tts_ws(ws):
        with client.realtime.tts.connect_multi_stream() as conn:
            stream = conn.open_stream(config=_config("done"))
            list(stream.receive_events())
            # Same stream_id can be re-opened after termination.
            conn.open_stream(config=_config("done"))


def test_multiplexed_audio_chunks_yields_decoded_bytes(client: SonioxClient) -> None:
    ws = MockWebSocket()
    ws.push_recv({"stream_id": "a", "audio": _AUDIO_B64})
    ws.push_recv({"stream_id": "a", "terminated": True})
    ws.close_after_recv()

    with _patch_sync_tts_ws(ws):
        with client.realtime.tts.connect_multi_stream() as conn:
            stream = conn.open_stream(config=_config("a"))
            chunks = list(stream.receive_audio_chunks())

    assert chunks == [_AUDIO_BYTES]


def test_multiplexed_audio_chunks_raises_on_invalid_base64(client: SonioxClient) -> None:
    ws = MockWebSocket()
    ws.push_recv({"stream_id": "a", "audio": "not-base64!@#"})
    ws.close_after_recv()

    with _patch_sync_tts_ws(ws):
        with client.realtime.tts.connect_multi_stream() as conn:
            stream = conn.open_stream(config=_config("a"))
            with pytest.raises(SonioxRealtimeError, match="Invalid"):
                list(stream.receive_audio_chunks())


def test_multiplexed_receive_event_returns_none_on_close(client: SonioxClient) -> None:
    ws = MockWebSocket()
    ws.close_after_recv()

    with _patch_sync_tts_ws(ws):
        with client.realtime.tts.connect_multi_stream() as conn:
            stream = conn.open_stream(config=_config("a"))
            assert stream.receive_event() is None


def test_multiplexed_send_failure_wraps_as_realtime_error(client: SonioxClient) -> None:
    ws = MockWebSocket()
    ws.close_after_recv()

    with _patch_sync_tts_ws(ws):
        with client.realtime.tts.connect_multi_stream() as conn:
            stream = conn.open_stream(config=_config("a"))
            ws.closed = True
            with pytest.raises(SonioxRealtimeError, match="Failed to send"):
                stream.send_text_chunk("after-close")


def test_multiplexed_close_disconnects_connection(client: SonioxClient) -> None:
    """After ``close()``, the connection is no longer usable for new streams."""
    ws = MockWebSocket()
    ws.close_after_recv()

    with _patch_sync_tts_ws(ws):
        conn = client.realtime.tts.connect_multi_stream()
        with conn:
            conn.open_stream(config=_config("a"))
            conn.close()
            with pytest.raises(SonioxRealtimeError, match="not connected"):
                conn.open_stream(config=_config("b"))


def test_multiplexed_last_message_tracks_most_recent(client: SonioxClient) -> None:
    ws = MockWebSocket()
    ws.push_recv({"stream_id": "a", "audio": _AUDIO_B64})
    ws.push_recv({"stream_id": "a", "terminated": True})
    ws.close_after_recv()

    with _patch_sync_tts_ws(ws):
        with client.realtime.tts.connect_multi_stream() as conn:
            stream = conn.open_stream(config=_config("a"))
            assert conn.last_message is None
            list(stream.receive_events())
            assert conn.last_message is not None
            assert stream.last_message is not None
            assert stream.last_message.terminated is True
            assert stream.config.stream_id == "a"
            assert stream.stream_id == "a"
