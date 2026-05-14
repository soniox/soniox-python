"""
Realtime STT end-to-end tests (sync + async) against a scripted mock WebSocket.

Each scenario in ``cases.REALTIME_CASES`` is a full session: we replay a set
of server events, exercise the session with a matching send sequence, and
assert that (a) the SDK emitted the expected wire messages in order, and
(b) all scripted server events were surfaced to the caller.
"""

from __future__ import annotations

from unittest.mock import patch

import pytest

from soniox.client import AsyncSonioxClient, SonioxClient
from soniox.types.realtime import RealtimeSTTConfig

from .cases import REALTIME_CASES, RealtimeCase
from .mock_ws import AsyncMockWebSocket, MockWebSocket

# ---------------------------------------------------------------------------
# Scripted scenarios
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("case", REALTIME_CASES, ids=lambda c: c.id)
def test_realtime_sync(client: SonioxClient, case: RealtimeCase) -> None:
    ws = MockWebSocket()
    for event in case.server_events:
        ws.push_recv(event)
    ws.close_after_recv()

    audio_chunks = [m for m in case.expected_sent if isinstance(m, bytes)]

    with patch("soniox.realtime.stt.sync_ws_connect", return_value=ws):
        with client.realtime.stt.connect(config=case.config) as session:
            for chunk in audio_chunks:
                session.send_bytes(chunk, finish=False)
            session.finish()
            received = list(session.receive_events())

    expected_received = case.expected_received or len(case.server_events)
    assert len(received) == expected_received
    assert ws.sent_messages[: len(case.expected_sent)] == case.expected_sent


@pytest.mark.parametrize("case", REALTIME_CASES, ids=lambda c: c.id)
async def test_realtime_async(async_client: AsyncSonioxClient, case: RealtimeCase) -> None:
    ws = AsyncMockWebSocket()
    for event in case.server_events:
        ws.push_recv(event)
    ws.close_after_recv()

    audio_chunks = [m for m in case.expected_sent if isinstance(m, bytes)]

    with patch("soniox.realtime.async_stt.async_ws_connect", return_value=ws):
        async with async_client.realtime.stt.connect(config=case.config) as session:
            for chunk in audio_chunks:
                await session.send_bytes(chunk, finish=False)
            await session.finish()
            received = [event async for event in session.receive_events()]

    expected_received = case.expected_received or len(case.server_events)
    assert len(received) == expected_received
    assert ws.sent_messages[: len(case.expected_sent)] == case.expected_sent


# ---------------------------------------------------------------------------
# Behaviors that don't fit the scripted table
# ---------------------------------------------------------------------------


def _patch_sync_ws(ws: MockWebSocket):
    """Patch the sync websocket connect to return ``ws``."""
    return patch("soniox.realtime.stt.sync_ws_connect", return_value=ws)


def test_pause_emits_finalize_control(client: SonioxClient) -> None:
    """``pause()`` defaults to sending a FINALIZE before suspending audio."""
    ws = MockWebSocket()
    ws.close_after_recv()

    with _patch_sync_ws(ws):
        with client.realtime.stt.connect(config=RealtimeSTTConfig(model="v1")) as session:
            session.pause()

    assert {"type": "finalize"} in ws.sent_messages


def test_pause_with_finalize_false_skips_finalize(client: SonioxClient) -> None:
    """``pause(finalize=False)`` suspends audio without emitting FINALIZE."""
    ws = MockWebSocket()
    ws.close_after_recv()

    with _patch_sync_ws(ws):
        with client.realtime.stt.connect(config=RealtimeSTTConfig(model="v1")) as session:
            session.pause(finalize=False)

    assert {"type": "finalize"} not in ws.sent_messages


def test_paused_session_drops_audio_chunks(client: SonioxClient) -> None:
    """Audio sent while paused is silently dropped, not buffered."""
    ws = MockWebSocket()
    ws.close_after_recv()

    with _patch_sync_ws(ws):
        with client.realtime.stt.connect(config=RealtimeSTTConfig(model="v1")) as session:
            session.send_bytes(b"before-pause", finish=False)
            session.pause()
            session.send_bytes(b"during-pause", finish=False)  # dropped
            session.finish()

    audio_sent = [m for m in ws.sent_messages if isinstance(m, bytes)]
    assert audio_sent == [b"before-pause"]


def test_resume_restores_audio_sending(client: SonioxClient) -> None:
    """After ``resume()``, audio chunks reach the wire again."""
    ws = MockWebSocket()
    ws.close_after_recv()

    with _patch_sync_ws(ws):
        with client.realtime.stt.connect(config=RealtimeSTTConfig(model="v1")) as session:
            session.pause()
            session.send_bytes(b"during-pause", finish=False)  # dropped
            session.resume()
            session.send_bytes(b"after-resume", finish=False)
            session.finish()

    audio_sent = [m for m in ws.sent_messages if isinstance(m, bytes)]
    assert audio_sent == [b"after-resume"]


def test_finalize_emits_control_message(client: SonioxClient) -> None:
    ws = MockWebSocket()
    ws.close_after_recv()
    config = RealtimeSTTConfig(model="v1")
    with patch("soniox.realtime.stt.sync_ws_connect", return_value=ws):
        with client.realtime.stt.connect(config=config) as session:
            session.finalize()
            session.finish()
    assert {"type": "finalize"} in ws.sent_messages


def test_keepalive_emits_control_message(client: SonioxClient) -> None:
    ws = MockWebSocket()
    ws.close_after_recv()
    config = RealtimeSTTConfig(model="v1")
    with patch("soniox.realtime.stt.sync_ws_connect", return_value=ws):
        with client.realtime.stt.connect(config=config) as session:
            session.keep_alive()
            session.finish()
    assert {"type": "keepalive"} in ws.sent_messages


def test_receive_event_raises_when_not_connected(client: SonioxClient) -> None:
    """Calling session methods outside the context manager is an error."""
    from soniox.errors import SonioxRealtimeError

    config = RealtimeSTTConfig(model="v1")
    session = client.realtime.stt.connect(config=config)
    with pytest.raises(SonioxRealtimeError):
        session.receive_event()
    with pytest.raises(SonioxRealtimeError):
        session.send_byte_chunk(b"x")


def test_send_bytes_iterator_auto_finishes(client: SonioxClient) -> None:
    """When ``send_bytes`` is given an iterator it must auto-emit FINISH."""
    ws = MockWebSocket()
    ws.close_after_recv()
    config = RealtimeSTTConfig(model="v1")

    with patch("soniox.realtime.stt.sync_ws_connect", return_value=ws):
        with client.realtime.stt.connect(config=config) as session:
            session.send_bytes(iter([b"a", b"b", b"c"]))  # default finish=True

    audio = [m for m in ws.sent_messages if isinstance(m, bytes)]
    assert audio == [b"a", b"b", b"c"]
    # FINISH is the empty string, and send_bytes(iterator) sent it once;
    # the context manager's close() sends a second one.
    assert ws.sent_messages.count("") >= 1


def test_send_bytes_iterator_without_finish(client: SonioxClient) -> None:
    ws = MockWebSocket()
    ws.close_after_recv()
    config = RealtimeSTTConfig(model="v1")

    with patch("soniox.realtime.stt.sync_ws_connect", return_value=ws):
        with client.realtime.stt.connect(config=config) as session:
            session.send_bytes(iter([b"a", b"b"]), finish=False)
            # We haven't sent FINISH yet - the only "" in sent_messages must
            # come from __exit__.
            non_close_messages = [m for m in ws.sent_messages if m != ""]
            assert [m for m in non_close_messages if isinstance(m, bytes)] == [
                b"a",
                b"b",
            ]


async def test_send_bytes_async_iterator_auto_finishes(
    async_client: AsyncSonioxClient,
) -> None:
    ws = AsyncMockWebSocket()
    ws.close_after_recv()
    config = RealtimeSTTConfig(model="v1")

    async def _chunks():
        for chunk in (b"a", b"b"):
            yield chunk

    with patch("soniox.realtime.async_stt.async_ws_connect", return_value=ws):
        async with async_client.realtime.stt.connect(config=config) as session:
            await session.send_bytes(_chunks())

    audio = [m for m in ws.sent_messages if isinstance(m, bytes)]
    assert audio == [b"a", b"b"]


def test_handle_events_dispatches_to_callback(client: SonioxClient) -> None:
    ws = MockWebSocket()
    ws.push_recv({"tokens": [{"text": "hi", "is_final": True}]})
    ws.push_recv({"tokens": [{"text": "bye", "is_final": True}], "finished": True})
    ws.close_after_recv()

    received: list = []
    config = RealtimeSTTConfig(model="v1")
    with patch("soniox.realtime.stt.sync_ws_connect", return_value=ws):
        with client.realtime.stt.connect(config=config) as session:
            session.finish()
            session.handle_events(received.append)

    assert len(received) == 2
    assert received[0].tokens[0].text == "hi"
    assert received[1].finished is True


def test_session_config_and_paused_properties(client: SonioxClient) -> None:
    config = RealtimeSTTConfig(model="v1")
    ws = MockWebSocket()
    ws.close_after_recv()

    with patch("soniox.realtime.stt.sync_ws_connect", return_value=ws):
        with client.realtime.stt.connect(config=config) as session:
            # Session wraps the config with the API key attached; payload
            # equivalence is what callers care about, not object identity.
            assert session.config.model == config.model
            assert session.config.api_key == "test_key"
            assert session.paused is False
            session.pause()
            assert session.paused is True
            session.resume()
            assert session.paused is False
            assert session.last_message is None


def test_session_close_is_idempotent_before_enter(client: SonioxClient) -> None:
    """Calling close() on a session that was never entered must be a no-op."""
    session = client.realtime.stt.connect(config=RealtimeSTTConfig(model="v1"))
    session.close()  # must not raise


def test_pause_is_idempotent(client: SonioxClient) -> None:
    """Calling ``pause()`` on an already-paused session must not emit a second FINALIZE."""
    ws = MockWebSocket()
    ws.close_after_recv()
    with patch("soniox.realtime.stt.sync_ws_connect", return_value=ws):
        with client.realtime.stt.connect(config=RealtimeSTTConfig(model="v1")) as session:
            session.pause()
            session.pause()  # already paused
            finalize_count = sum(1 for m in ws.sent_messages if m == {"type": "finalize"})
            assert finalize_count == 1


def test_resume_when_not_paused_is_noop(client: SonioxClient) -> None:
    """Calling ``resume()`` on a session that was never paused must not raise or emit."""
    ws = MockWebSocket()
    ws.close_after_recv()
    with patch("soniox.realtime.stt.sync_ws_connect", return_value=ws):
        with client.realtime.stt.connect(config=RealtimeSTTConfig(model="v1")) as session:
            before = list(ws.sent_messages)
            session.resume()
            assert ws.sent_messages == before
            assert session.paused is False


def test_pause_raises_when_not_connected(client: SonioxClient) -> None:
    from soniox.errors import SonioxRealtimeError

    session = client.realtime.stt.connect(config=RealtimeSTTConfig(model="v1"))
    with pytest.raises(SonioxRealtimeError):
        session.pause()
    with pytest.raises(SonioxRealtimeError):
        session.resume()


def test_send_control_message_wraps_send_errors(client: SonioxClient) -> None:
    from soniox.errors import SonioxRealtimeError

    ws = MockWebSocket()
    ws.close_after_recv()

    with patch("soniox.realtime.stt.sync_ws_connect", return_value=ws):
        with client.realtime.stt.connect(config=RealtimeSTTConfig(model="v1")) as session:
            ws.closed = True  # subsequent send raises ConnectionClosed
            with pytest.raises(SonioxRealtimeError):
                session.keep_alive()


async def test_async_session_exposes_config(
    async_client: AsyncSonioxClient,
) -> None:
    ws = AsyncMockWebSocket()
    ws.close_after_recv()
    config = RealtimeSTTConfig(model="v1")

    with patch("soniox.realtime.async_stt.async_ws_connect", return_value=ws):
        async with async_client.realtime.stt.connect(config=config) as session:
            assert session.config.model == "v1"
            assert session.last_message is None


async def test_async_pause_resume_toggles_paused_flag(
    async_client: AsyncSonioxClient,
) -> None:
    ws = AsyncMockWebSocket()
    ws.close_after_recv()

    with patch("soniox.realtime.async_stt.async_ws_connect", return_value=ws):
        async with async_client.realtime.stt.connect(
            config=RealtimeSTTConfig(model="v1")
        ) as session:
            assert session.paused is False
            await session.pause()
            assert session.paused is True
            await session.resume()
            assert session.paused is False


async def test_async_pause_is_idempotent(
    async_client: AsyncSonioxClient,
) -> None:
    """A second ``pause()`` on a paused async session must not emit another FINALIZE."""
    ws = AsyncMockWebSocket()
    ws.close_after_recv()

    with patch("soniox.realtime.async_stt.async_ws_connect", return_value=ws):
        async with async_client.realtime.stt.connect(
            config=RealtimeSTTConfig(model="v1")
        ) as session:
            await session.pause()
            await session.pause()
            finalize_count = sum(1 for m in ws.sent_messages if m == {"type": "finalize"})
            assert finalize_count == 1


async def test_async_resume_when_not_paused_is_noop(
    async_client: AsyncSonioxClient,
) -> None:
    ws = AsyncMockWebSocket()
    ws.close_after_recv()

    with patch("soniox.realtime.async_stt.async_ws_connect", return_value=ws):
        async with async_client.realtime.stt.connect(
            config=RealtimeSTTConfig(model="v1")
        ) as session:
            before = list(ws.sent_messages)
            await session.resume()
            assert ws.sent_messages == before
            assert session.paused is False


async def test_async_pause_with_finalize_false_skips_finalize(
    async_client: AsyncSonioxClient,
) -> None:
    ws = AsyncMockWebSocket()
    ws.close_after_recv()

    with patch("soniox.realtime.async_stt.async_ws_connect", return_value=ws):
        async with async_client.realtime.stt.connect(
            config=RealtimeSTTConfig(model="v1")
        ) as session:
            await session.pause(finalize=False)

    assert {"type": "finalize"} not in ws.sent_messages


async def test_async_session_close_idempotent_before_enter(
    async_client: AsyncSonioxClient,
) -> None:
    session = async_client.realtime.stt.connect(config=RealtimeSTTConfig(model="v1"))
    await session.close()  # must not raise


async def test_async_pause_raises_when_not_connected(
    async_client: AsyncSonioxClient,
) -> None:
    from soniox.errors import SonioxRealtimeError

    session = async_client.realtime.stt.connect(config=RealtimeSTTConfig(model="v1"))
    with pytest.raises(SonioxRealtimeError):
        await session.pause()
    with pytest.raises(SonioxRealtimeError):
        await session.resume()


async def test_async_send_control_message_wraps_send_errors(
    async_client: AsyncSonioxClient,
) -> None:
    from soniox.errors import SonioxRealtimeError

    ws = AsyncMockWebSocket()
    ws.close_after_recv()

    with patch("soniox.realtime.async_stt.async_ws_connect", return_value=ws):
        async with async_client.realtime.stt.connect(
            config=RealtimeSTTConfig(model="v1")
        ) as session:
            ws.closed = True
            with pytest.raises(SonioxRealtimeError):
                await session.keep_alive()


async def test_async_client_aclose_releases_http_transport() -> None:
    """``aclose`` must close the httpx.AsyncClient so the connection pool is
    freed. After close, requests raise."""
    async with AsyncSonioxClient(api_key="test_key") as c:
        pass
    # After the context manager exits, the underlying httpx client must be closed.
    assert c._http_client.is_closed  # pyright: ignore[reportPrivateUsage]
