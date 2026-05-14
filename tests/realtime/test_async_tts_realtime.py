"""
Realtime Text-to-Speech tests (async) - mirrors :mod:`tests.realtime.test_tts_realtime`.
"""

from __future__ import annotations

import base64
from unittest.mock import patch

import pytest

from soniox.client import AsyncSonioxClient
from soniox.errors import SonioxRealtimeError
from soniox.realtime._constants import MAX_TTS_STREAMS_PER_CONNECTION
from soniox.types.realtime import RealtimeTTSConfig

from .mock_ws import AsyncMockWebSocket

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


def _patch_async_tts_ws(ws: AsyncMockWebSocket):
    return patch("soniox.realtime.async_tts.async_ws_connect", return_value=ws)


async def _aiter(items):
    for item in items:
        yield item


# ---------------------------------------------------------------------------
# Single-stream connection
# ---------------------------------------------------------------------------


async def test_async_connect_sends_config_on_enter(async_client: AsyncSonioxClient) -> None:
    ws = AsyncMockWebSocket()
    ws.close_after_recv()

    with _patch_async_tts_ws(ws):
        async with async_client.realtime.tts.connect(config=_config()) as _:
            pass

    config_msg = ws.sent_messages[0]
    assert config_msg["stream_id"] == "s1"
    assert config_msg["model"] == "m"
    assert config_msg["api_key"] == "test_key"


async def test_async_connect_raises_on_ws_failure(async_client: AsyncSonioxClient) -> None:
    with patch(
        "soniox.realtime.async_tts.async_ws_connect", side_effect=ConnectionError("boom")
    ):
        with pytest.raises(SonioxRealtimeError, match="Failed to start"):
            async with async_client.realtime.tts.connect(config=_config()):
                pass


async def test_async_send_text_chunk_emits_payload(
    async_client: AsyncSonioxClient,
) -> None:
    ws = AsyncMockWebSocket()
    ws.close_after_recv()

    with _patch_async_tts_ws(ws):
        async with async_client.realtime.tts.connect(config=_config()) as conn:
            await conn.send_text_chunk("hello", text_end=False)

    text_msgs = [m for m in ws.sent_messages if isinstance(m, dict) and m.get("text") == "hello"]
    assert text_msgs == [{"text": "hello", "text_end": False, "stream_id": "s1"}]


async def test_async_send_text_chunks_string(async_client: AsyncSonioxClient) -> None:
    ws = AsyncMockWebSocket()
    ws.close_after_recv()

    with _patch_async_tts_ws(ws):
        async with async_client.realtime.tts.connect(config=_config()) as conn:
            await conn.send_text_chunks("done", text_end=True)

    text_msgs = [m for m in ws.sent_messages if isinstance(m, dict) and "text" in m]
    assert text_msgs == [{"text": "done", "text_end": True, "stream_id": "s1"}]


async def test_async_send_text_chunks_iterator(async_client: AsyncSonioxClient) -> None:
    ws = AsyncMockWebSocket()
    ws.close_after_recv()

    with _patch_async_tts_ws(ws):
        async with async_client.realtime.tts.connect(config=_config()) as conn:
            await conn.send_text_chunks(_aiter(["a", "b", "c"]))

    text_msgs = [m for m in ws.sent_messages if isinstance(m, dict) and "text" in m]
    assert [p["text"] for p in text_msgs] == ["a", "b", "c", ""]
    assert text_msgs[-1]["text_end"] is True


async def test_async_send_text_chunks_iterator_without_end(
    async_client: AsyncSonioxClient,
) -> None:
    ws = AsyncMockWebSocket()
    ws.close_after_recv()

    with _patch_async_tts_ws(ws):
        async with async_client.realtime.tts.connect(config=_config()) as conn:
            await conn.send_text_chunks(_aiter(["a", "b"]), text_end=False)

    text_msgs = [m for m in ws.sent_messages if isinstance(m, dict) and "text" in m]
    assert [p["text"] for p in text_msgs] == ["a", "b"]
    assert all(not p["text_end"] for p in text_msgs)


async def test_async_finish_sends_text_end(async_client: AsyncSonioxClient) -> None:
    ws = AsyncMockWebSocket()
    ws.close_after_recv()

    with _patch_async_tts_ws(ws):
        async with async_client.realtime.tts.connect(config=_config()) as conn:
            await conn.finish()

    finish_msgs = [
        m for m in ws.sent_messages
        if isinstance(m, dict) and m.get("text_end") is True and m.get("text") == ""
    ]
    assert len(finish_msgs) == 1


async def test_async_cancel_sends_payload(async_client: AsyncSonioxClient) -> None:
    ws = AsyncMockWebSocket()
    ws.close_after_recv()

    with _patch_async_tts_ws(ws):
        async with async_client.realtime.tts.connect(config=_config()) as conn:
            await conn.cancel()

    assert {"stream_id": "s1", "cancel": True} in ws.sent_messages


async def test_async_keep_alive_sends_payload(async_client: AsyncSonioxClient) -> None:
    ws = AsyncMockWebSocket()
    ws.close_after_recv()

    with _patch_async_tts_ws(ws):
        async with async_client.realtime.tts.connect(config=_config()) as conn:
            await conn.keep_alive()

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
async def test_async_method_raises_when_not_connected(
    async_client: AsyncSonioxClient, method: str, args: tuple
) -> None:
    conn = async_client.realtime.tts.connect(config=_config())
    with pytest.raises(SonioxRealtimeError, match="not connected"):
        await getattr(conn, method)(*args)


async def test_async_send_text_chunk_wraps_send_errors(
    async_client: AsyncSonioxClient,
) -> None:
    ws = AsyncMockWebSocket()
    ws.close_after_recv()

    with _patch_async_tts_ws(ws):
        async with async_client.realtime.tts.connect(config=_config()) as conn:
            ws.closed = True
            with pytest.raises(SonioxRealtimeError, match="Failed to send text chunk"):
                await conn.send_text_chunk("hi")


async def test_async_cancel_wraps_send_errors(async_client: AsyncSonioxClient) -> None:
    ws = AsyncMockWebSocket()
    ws.close_after_recv()

    with _patch_async_tts_ws(ws):
        async with async_client.realtime.tts.connect(config=_config()) as conn:
            ws.closed = True
            with pytest.raises(SonioxRealtimeError, match="Failed to cancel"):
                await conn.cancel()


async def test_async_keep_alive_wraps_send_errors(
    async_client: AsyncSonioxClient,
) -> None:
    ws = AsyncMockWebSocket()
    ws.close_after_recv()

    with _patch_async_tts_ws(ws):
        async with async_client.realtime.tts.connect(config=_config()) as conn:
            ws.closed = True
            with pytest.raises(SonioxRealtimeError, match="Failed to send keep-alive"):
                await conn.keep_alive()


async def test_async_pause_suspends_sending(async_client: AsyncSonioxClient) -> None:
    ws = AsyncMockWebSocket()
    ws.close_after_recv()

    with _patch_async_tts_ws(ws):
        async with async_client.realtime.tts.connect(config=_config()) as conn:
            await conn.send_text_chunk("before", text_end=False)
            await conn.pause()
            assert conn.paused is True
            await conn.send_text_chunk("during", text_end=False)
            await conn.resume()
            assert conn.paused is False
            await conn.send_text_chunk("after", text_end=False)

    sent_texts = [
        m["text"] for m in ws.sent_messages
        if isinstance(m, dict) and "text" in m
    ]
    assert sent_texts == ["before", "after"]


async def test_async_pause_idempotent(async_client: AsyncSonioxClient) -> None:
    ws = AsyncMockWebSocket()
    ws.close_after_recv()

    with _patch_async_tts_ws(ws):
        async with async_client.realtime.tts.connect(config=_config()) as conn:
            await conn.pause()
            await conn.pause()
            assert conn.paused is True


async def test_async_resume_when_not_paused_noop(
    async_client: AsyncSonioxClient,
) -> None:
    ws = AsyncMockWebSocket()
    ws.close_after_recv()

    with _patch_async_tts_ws(ws):
        async with async_client.realtime.tts.connect(config=_config()) as conn:
            await conn.resume()
            assert conn.paused is False


async def test_async_receive_event_returns_audio(
    async_client: AsyncSonioxClient,
) -> None:
    ws = AsyncMockWebSocket()
    ws.push_recv({"audio": _AUDIO_B64})
    ws.close_after_recv()

    with _patch_async_tts_ws(ws):
        async with async_client.realtime.tts.connect(config=_config()) as conn:
            event = await conn.receive_event()

    assert event is not None
    assert event.audio_bytes() == _AUDIO_BYTES


async def test_async_receive_event_returns_none_on_close(
    async_client: AsyncSonioxClient,
) -> None:
    ws = AsyncMockWebSocket()
    ws.close_after_recv()

    with _patch_async_tts_ws(ws):
        async with async_client.realtime.tts.connect(config=_config()) as conn:
            event = await conn.receive_event()

    assert event is None


async def test_async_receive_event_raises_on_error(
    async_client: AsyncSonioxClient,
) -> None:
    ws = AsyncMockWebSocket()
    ws.push_recv({"error_code": 500, "error_message": "boom"})
    ws.close_after_recv()

    with _patch_async_tts_ws(ws):
        async with async_client.realtime.tts.connect(config=_config()) as conn:
            with pytest.raises(SonioxRealtimeError, match="boom"):
                await conn.receive_event()


async def test_async_receive_event_default_message(
    async_client: AsyncSonioxClient,
) -> None:
    ws = AsyncMockWebSocket()
    ws.push_recv({"error_code": 500})
    ws.close_after_recv()

    with _patch_async_tts_ws(ws):
        async with async_client.realtime.tts.connect(config=_config()) as conn:
            with pytest.raises(SonioxRealtimeError, match="code 500"):
                await conn.receive_event()


async def test_async_receive_events_stops_on_terminated(
    async_client: AsyncSonioxClient,
) -> None:
    ws = AsyncMockWebSocket()
    ws.push_recv({"audio": _AUDIO_B64})
    ws.push_recv({"audio_end": True})
    ws.push_recv({"terminated": True})
    ws.push_recv({"audio": _AUDIO_B64})  # not reached
    ws.close_after_recv()

    with _patch_async_tts_ws(ws):
        async with async_client.realtime.tts.connect(config=_config()) as conn:
            events = [e async for e in conn.receive_events()]

    assert len(events) == 3
    assert events[-1].terminated is True


async def test_async_receive_audio_chunks(async_client: AsyncSonioxClient) -> None:
    ws = AsyncMockWebSocket()
    ws.push_recv({"audio": _AUDIO_B64})
    ws.push_recv({"audio": _AUDIO_B64, "terminated": True})
    ws.close_after_recv()

    with _patch_async_tts_ws(ws):
        async with async_client.realtime.tts.connect(config=_config()) as conn:
            chunks = [c async for c in conn.receive_audio_chunks()]

    assert chunks == [_AUDIO_BYTES, _AUDIO_BYTES]


async def test_async_audio_chunks_invalid_base64(
    async_client: AsyncSonioxClient,
) -> None:
    ws = AsyncMockWebSocket()
    ws.push_recv({"audio": "not-base64!@#"})
    ws.close_after_recv()

    with _patch_async_tts_ws(ws):
        async with async_client.realtime.tts.connect(config=_config()) as conn:
            with pytest.raises(SonioxRealtimeError, match="Invalid"):
                async for _ in conn.receive_audio_chunks():
                    pass


async def test_async_handle_events_invokes_handler(
    async_client: AsyncSonioxClient,
) -> None:
    ws = AsyncMockWebSocket()
    ws.push_recv({"audio": _AUDIO_B64})
    ws.push_recv({"terminated": True})
    ws.close_after_recv()
    seen: list = []

    async def _handler(event):
        seen.append(event)

    with _patch_async_tts_ws(ws):
        async with async_client.realtime.tts.connect(config=_config()) as conn:
            await conn.handle_events(_handler)

    assert len(seen) == 2
    assert seen[-1].terminated is True


async def test_async_last_message_tracking(async_client: AsyncSonioxClient) -> None:
    ws = AsyncMockWebSocket()
    ws.push_recv({"audio": _AUDIO_B64})
    ws.push_recv({"terminated": True})
    ws.close_after_recv()

    with _patch_async_tts_ws(ws):
        async with async_client.realtime.tts.connect(config=_config()) as conn:
            assert conn.last_message is None
            [_ async for _ in conn.receive_events()]
            assert conn.last_message is not None
            assert conn.last_message.terminated is True


async def test_async_receive_event_recv_timeout(
    async_client: AsyncSonioxClient,
) -> None:
    ws = AsyncMockWebSocket()
    ws.push_recv_error(TimeoutError("slow"))

    with _patch_async_tts_ws(ws):
        async with async_client.realtime.tts.connect(config=_config()) as conn:
            with pytest.raises(SonioxRealtimeError, match="Timed out"):
                await conn.receive_event()


async def test_async_close_idempotent_after_exit(
    async_client: AsyncSonioxClient,
) -> None:
    ws = AsyncMockWebSocket()
    ws.close_after_recv()

    with _patch_async_tts_ws(ws):
        async with async_client.realtime.tts.connect(config=_config()) as conn:
            pass
        await conn.close()


async def test_async_close_before_enter_noop(
    async_client: AsyncSonioxClient,
) -> None:
    conn = async_client.realtime.tts.connect(config=_config())
    await conn.close()


# ---------------------------------------------------------------------------
# Multiplexed connection
# ---------------------------------------------------------------------------


async def test_async_multiplexed_no_send_until_open_stream(
    async_client: AsyncSonioxClient,
) -> None:
    ws = AsyncMockWebSocket()
    ws.close_after_recv()

    with _patch_async_tts_ws(ws):
        async with async_client.realtime.tts.connect_multi_stream() as _:
            pass

    assert ws.sent_messages == []


async def test_async_multiplexed_connect_wraps_ws_failure(
    async_client: AsyncSonioxClient,
) -> None:
    with patch(
        "soniox.realtime.async_tts.async_ws_connect", side_effect=ConnectionError("nope")
    ):
        with pytest.raises(SonioxRealtimeError, match="Failed to start"):
            async with async_client.realtime.tts.connect_multi_stream():
                pass


async def test_async_open_stream_sends_config(
    async_client: AsyncSonioxClient,
) -> None:
    ws = AsyncMockWebSocket()
    ws.close_after_recv()

    with _patch_async_tts_ws(ws):
        async with async_client.realtime.tts.connect_multi_stream() as conn:
            await conn.open_stream(config=_config("alpha"))

    config_msgs = [
        m for m in ws.sent_messages
        if isinstance(m, dict) and m.get("stream_id") == "alpha" and "model" in m
    ]
    assert len(config_msgs) == 1


async def test_async_open_stream_rejects_duplicate(
    async_client: AsyncSonioxClient,
) -> None:
    ws = AsyncMockWebSocket()
    ws.close_after_recv()

    with _patch_async_tts_ws(ws):
        async with async_client.realtime.tts.connect_multi_stream() as conn:
            await conn.open_stream(config=_config("alpha"))
            with pytest.raises(SonioxRealtimeError, match="already active"):
                await conn.open_stream(config=_config("alpha"))


async def test_async_open_stream_rejects_at_limit(
    async_client: AsyncSonioxClient,
) -> None:
    ws = AsyncMockWebSocket()
    ws.close_after_recv()

    with _patch_async_tts_ws(ws):
        async with async_client.realtime.tts.connect_multi_stream() as conn:
            for i in range(MAX_TTS_STREAMS_PER_CONNECTION):
                await conn.open_stream(config=_config(f"s{i}"))
            with pytest.raises(SonioxRealtimeError, match="Maximum"):
                await conn.open_stream(config=_config("overflow"))


async def test_async_open_stream_raises_when_not_connected(
    async_client: AsyncSonioxClient,
) -> None:
    conn = async_client.realtime.tts.connect_multi_stream()
    with pytest.raises(SonioxRealtimeError, match="not connected"):
        await conn.open_stream(config=_config())


async def test_async_multiplexed_routes_events(
    async_client: AsyncSonioxClient,
) -> None:
    ws = AsyncMockWebSocket()
    ws.push_recv({"stream_id": "a", "audio": _AUDIO_B64})
    ws.push_recv({"stream_id": "b", "audio": _AUDIO_B64})
    ws.push_recv({"stream_id": "a", "terminated": True})
    ws.push_recv({"stream_id": "b", "terminated": True})
    ws.close_after_recv()

    with _patch_async_tts_ws(ws):
        async with async_client.realtime.tts.connect_multi_stream() as conn:
            stream_a = await conn.open_stream(config=_config("a"))
            stream_b = await conn.open_stream(config=_config("b"))
            events_a = [e async for e in stream_a.receive_events()]
            events_b = [e async for e in stream_b.receive_events()]

    assert {e.stream_id for e in events_a} == {"a"}
    assert {e.stream_id for e in events_b} == {"b"}


async def test_async_stream_send_methods_emit(
    async_client: AsyncSonioxClient,
) -> None:
    ws = AsyncMockWebSocket()
    ws.close_after_recv()

    with _patch_async_tts_ws(ws):
        async with async_client.realtime.tts.connect_multi_stream() as conn:
            stream = await conn.open_stream(config=_config("zeta"))
            await stream.send_text_chunk("hi")
            await stream.send_text_chunks("done", text_end=True)
            await stream.send_text_chunks(_aiter(["x", "y"]))
            await stream.cancel()
            await stream.keep_alive()

    text_msgs = [m for m in ws.sent_messages if isinstance(m, dict) and "text" in m]
    cancel_msgs = [m for m in ws.sent_messages if isinstance(m, dict) and m.get("cancel")]
    assert all(m["stream_id"] == "zeta" for m in text_msgs)
    assert {"stream_id": "zeta", "cancel": True} in cancel_msgs
    assert {"keep_alive": True} in ws.sent_messages


async def test_async_stream_pause_drops_chunks(
    async_client: AsyncSonioxClient,
) -> None:
    ws = AsyncMockWebSocket()
    ws.close_after_recv()

    with _patch_async_tts_ws(ws):
        async with async_client.realtime.tts.connect_multi_stream() as conn:
            stream = await conn.open_stream(config=_config("p"))
            await stream.send_text_chunk("before")
            await stream.pause()
            await stream.send_text_chunk("during")
            await stream.resume()
            await stream.send_text_chunk("after")

    sent_texts = [
        m["text"] for m in ws.sent_messages
        if isinstance(m, dict) and "text" in m
    ]
    assert sent_texts == ["before", "after"]


async def test_async_multiplexed_pause_idempotent_resume_noop(
    async_client: AsyncSonioxClient,
) -> None:
    ws = AsyncMockWebSocket()
    ws.close_after_recv()

    with _patch_async_tts_ws(ws):
        async with async_client.realtime.tts.connect_multi_stream() as conn:
            await conn.resume()
            await conn.pause()
            await conn.pause()
            assert conn.paused is True


@pytest.mark.parametrize("method", ["pause", "resume"])
async def test_async_multiplexed_method_raises_when_not_connected(
    async_client: AsyncSonioxClient, method: str
) -> None:
    conn = async_client.realtime.tts.connect_multi_stream()
    with pytest.raises(SonioxRealtimeError, match="not connected"):
        await getattr(conn, method)()


async def test_async_multiplexed_global_error(
    async_client: AsyncSonioxClient,
) -> None:
    ws = AsyncMockWebSocket()
    ws.push_recv({"error_code": 500, "error_message": "global"})
    ws.close_after_recv()

    with _patch_async_tts_ws(ws):
        async with async_client.realtime.tts.connect_multi_stream() as conn:
            stream = await conn.open_stream(config=_config("only"))
            with pytest.raises(SonioxRealtimeError, match="global"):
                await stream.receive_event()


async def test_async_multiplexed_per_stream_error_deactivates(
    async_client: AsyncSonioxClient,
) -> None:
    ws = AsyncMockWebSocket()
    ws.push_recv({"stream_id": "boom", "error_code": 42, "error_message": "fail"})
    ws.close_after_recv()

    with _patch_async_tts_ws(ws):
        async with async_client.realtime.tts.connect_multi_stream() as conn:
            stream = await conn.open_stream(config=_config("boom"))
            with pytest.raises(SonioxRealtimeError, match="fail"):
                await stream.receive_event()
            await conn.open_stream(config=_config("boom"))


async def test_async_multiplexed_terminated_deactivates(
    async_client: AsyncSonioxClient,
) -> None:
    ws = AsyncMockWebSocket()
    ws.push_recv({"stream_id": "done", "terminated": True})
    ws.close_after_recv()

    with _patch_async_tts_ws(ws):
        async with async_client.realtime.tts.connect_multi_stream() as conn:
            stream = await conn.open_stream(config=_config("done"))
            [_ async for _ in stream.receive_events()]
            await conn.open_stream(config=_config("done"))


async def test_async_multiplexed_audio_chunks(
    async_client: AsyncSonioxClient,
) -> None:
    ws = AsyncMockWebSocket()
    ws.push_recv({"stream_id": "a", "audio": _AUDIO_B64})
    ws.push_recv({"stream_id": "a", "terminated": True})
    ws.close_after_recv()

    with _patch_async_tts_ws(ws):
        async with async_client.realtime.tts.connect_multi_stream() as conn:
            stream = await conn.open_stream(config=_config("a"))
            chunks = [c async for c in stream.receive_audio_chunks()]

    assert chunks == [_AUDIO_BYTES]


async def test_async_multiplexed_audio_chunks_invalid_base64(
    async_client: AsyncSonioxClient,
) -> None:
    ws = AsyncMockWebSocket()
    ws.push_recv({"stream_id": "a", "audio": "not-base64!@#"})
    ws.close_after_recv()

    with _patch_async_tts_ws(ws):
        async with async_client.realtime.tts.connect_multi_stream() as conn:
            stream = await conn.open_stream(config=_config("a"))
            with pytest.raises(SonioxRealtimeError, match="Invalid"):
                async for _ in stream.receive_audio_chunks():
                    pass


async def test_async_multiplexed_close_disconnects_connection(
    async_client: AsyncSonioxClient,
) -> None:
    ws = AsyncMockWebSocket()
    ws.close_after_recv()

    with _patch_async_tts_ws(ws):
        conn = async_client.realtime.tts.connect_multi_stream()
        async with conn:
            await conn.open_stream(config=_config("a"))
            await conn.close()
            with pytest.raises(SonioxRealtimeError, match="not connected"):
                await conn.open_stream(config=_config("b"))


async def test_async_multiplexed_send_after_close_raises(
    async_client: AsyncSonioxClient,
) -> None:
    ws = AsyncMockWebSocket()
    ws.close_after_recv()

    with _patch_async_tts_ws(ws):
        async with async_client.realtime.tts.connect_multi_stream() as conn:
            stream = await conn.open_stream(config=_config("x"))
        with pytest.raises(SonioxRealtimeError, match="not connected"):
            await stream.send_text_chunk("after-close")


async def test_async_multiplexed_send_failure_wraps(
    async_client: AsyncSonioxClient,
) -> None:
    ws = AsyncMockWebSocket()
    ws.close_after_recv()

    with _patch_async_tts_ws(ws):
        async with async_client.realtime.tts.connect_multi_stream() as conn:
            stream = await conn.open_stream(config=_config("a"))
            ws.closed = True
            with pytest.raises(SonioxRealtimeError, match="Failed to send"):
                await stream.send_text_chunk("after-close")


async def test_async_multiplexed_last_message(
    async_client: AsyncSonioxClient,
) -> None:
    ws = AsyncMockWebSocket()
    ws.push_recv({"stream_id": "a", "audio": _AUDIO_B64})
    ws.push_recv({"stream_id": "a", "terminated": True})
    ws.close_after_recv()

    with _patch_async_tts_ws(ws):
        async with async_client.realtime.tts.connect_multi_stream() as conn:
            stream = await conn.open_stream(config=_config("a"))
            assert conn.last_message is None
            [_ async for _ in stream.receive_events()]
            assert conn.last_message is not None
            assert stream.last_message is not None
            assert stream.last_message.terminated is True
            assert stream.config.stream_id == "a"
            assert stream.stream_id == "a"
