"""
Tests for :mod:`soniox.utils` - audio streaming helpers, token rendering, and
the background-thread audio sender.

These helpers are user-facing but never exercised indirectly elsewhere in the
suite, so they get dedicated coverage here.
"""

from __future__ import annotations

import io
import threading
import time
from pathlib import Path
from unittest.mock import patch

import pytest

from soniox.types import Token
from soniox.utils import (
    output_file_for_audio_format,
    render_tokens,
    start_audio_thread,
    start_text_thread,
    stream_audio,
    stream_audio_async,
    throttle_audio,
    throttle_audio_async,
)


# ---------------------------------------------------------------------------
# stream_audio (sync)
# ---------------------------------------------------------------------------


def test_stream_audio_from_bytes_splits_into_fixed_chunks() -> None:
    data = b"0123456789" * 10  # 100 bytes
    chunks = list(stream_audio(data, chunk_size_bytes=30))
    assert chunks == [data[:30], data[30:60], data[60:90], data[90:]]
    assert b"".join(chunks) == data


def test_stream_audio_from_bytes_short_source_yields_one_chunk() -> None:
    assert list(stream_audio(b"short", chunk_size_bytes=1024)) == [b"short"]


def test_stream_audio_from_empty_bytes_yields_nothing() -> None:
    assert list(stream_audio(b"", chunk_size_bytes=10)) == []


def test_stream_audio_from_stream_chunks_correctly() -> None:
    stream = io.BytesIO(b"abcdefghij")
    assert list(stream_audio(stream, chunk_size_bytes=3)) == [b"abc", b"def", b"ghi", b"j"]


def test_stream_audio_from_path(tmp_path: Path) -> None:
    audio_file = tmp_path / "clip.raw"
    audio_file.write_bytes(b"audio-content-from-disk")
    assert list(stream_audio(audio_file, chunk_size_bytes=5)) == [
        b"audio",
        b"-cont",
        b"ent-f",
        b"rom-d",
        b"isk",
    ]


def test_stream_audio_from_str_path(tmp_path: Path) -> None:
    audio_file = tmp_path / "clip.raw"
    audio_file.write_bytes(b"hello-world")
    assert list(stream_audio(str(audio_file), chunk_size_bytes=100)) == [b"hello-world"]


def test_stream_audio_rejects_non_positive_chunk_size() -> None:
    with pytest.raises(ValueError, match="chunk_size_bytes"):
        list(stream_audio(b"x", chunk_size_bytes=0))
    with pytest.raises(ValueError, match="chunk_size_bytes"):
        list(stream_audio(b"x", chunk_size_bytes=-1))


# ---------------------------------------------------------------------------
# stream_audio_async (async)
# ---------------------------------------------------------------------------


async def _collect(aiter) -> list[bytes]:
    return [chunk async for chunk in aiter]


async def test_stream_audio_async_from_bytes() -> None:
    data = b"0123456789" * 3  # 30 bytes
    chunks = await _collect(stream_audio_async(data, chunk_size_bytes=10))
    assert chunks == [data[:10], data[10:20], data[20:]]


async def test_stream_audio_async_from_path(tmp_path: Path) -> None:
    audio_file = tmp_path / "clip.raw"
    audio_file.write_bytes(b"async-content")
    chunks = await _collect(stream_audio_async(audio_file, chunk_size_bytes=5))
    assert b"".join(chunks) == b"async-content"


async def test_stream_audio_async_from_stream() -> None:
    chunks = await _collect(stream_audio_async(io.BytesIO(b"abcdef"), chunk_size_bytes=2))
    assert chunks == [b"ab", b"cd", b"ef"]


async def test_stream_audio_async_rejects_non_positive_chunk_size() -> None:
    with pytest.raises(ValueError, match="chunk_size_bytes"):
        await _collect(stream_audio_async(b"x", chunk_size_bytes=0))


# ---------------------------------------------------------------------------
# throttle_audio
# ---------------------------------------------------------------------------


def test_throttle_audio_yields_same_chunks_as_stream_audio() -> None:
    data = b"abcdef"
    assert list(throttle_audio(data, chunk_size_bytes=2, delay_seconds=0.0)) == [
        b"ab",
        b"cd",
        b"ef",
    ]


def test_throttle_audio_sleeps_between_chunks() -> None:
    data = b"abcdef"
    with patch("soniox.utils.time.sleep") as sleep_mock:
        list(throttle_audio(data, chunk_size_bytes=2, delay_seconds=0.1))
    # 3 chunks → 3 sleep calls, one after each yield
    assert sleep_mock.call_count == 3
    sleep_mock.assert_called_with(0.1)


def test_throttle_audio_zero_delay_skips_sleep() -> None:
    data = b"abcd"
    with patch("soniox.utils.time.sleep") as sleep_mock:
        list(throttle_audio(data, chunk_size_bytes=2, delay_seconds=0.0))
    sleep_mock.assert_not_called()


def test_throttle_audio_rejects_negative_delay() -> None:
    with pytest.raises(ValueError, match="delay_seconds"):
        list(throttle_audio(b"x", delay_seconds=-0.1))


async def test_throttle_audio_async_sleeps_between_chunks() -> None:
    async def fake_sleep(_: float) -> None:
        return None

    data = b"abcd"
    with patch("soniox.utils.asyncio.sleep", side_effect=fake_sleep) as sleep_mock:
        chunks = await _collect(
            throttle_audio_async(data, chunk_size_bytes=2, delay_seconds=0.1)
        )
    assert chunks == [b"ab", b"cd"]
    assert sleep_mock.call_count == 2


async def test_throttle_audio_async_rejects_negative_delay() -> None:
    with pytest.raises(ValueError, match="delay_seconds"):
        await _collect(throttle_audio_async(b"x", delay_seconds=-1))


# ---------------------------------------------------------------------------
# render_tokens
# ---------------------------------------------------------------------------


def _tok(**kwargs) -> Token:
    return Token(text=kwargs.pop("text", ""), **kwargs)


def test_render_tokens_concatenates_plain_text() -> None:
    tokens = [_tok(text="Hello"), _tok(text=" world")]
    assert render_tokens(tokens, []) == "Hello world"


def test_render_tokens_combines_final_and_non_final() -> None:
    final = [_tok(text="done.")]
    non_final = [_tok(text=" partial")]
    assert render_tokens(final, non_final) == "done. partial"


def test_render_tokens_renders_speaker_boundaries() -> None:
    tokens = [
        _tok(text="Hi.", speaker="1"),
        _tok(text=" Hello.", speaker="2"),
    ]
    out = render_tokens(tokens, [])
    # First speaker gets a label; second speaker is preceded by a blank line.
    assert "Speaker 1:" in out
    assert "\n\nSpeaker 2:" in out


def test_render_tokens_renders_language_tags() -> None:
    tokens = [
        _tok(text="Hello", language="en"),
        _tok(text="Bonjour", language="fr"),
    ]
    out = render_tokens(tokens, [])
    assert "[en]" in out
    assert "[fr]" in out


def test_render_tokens_marks_translations() -> None:
    tokens = [_tok(text="Bonjour", language="fr", translation_status="translation")]
    out = render_tokens(tokens, [])
    assert "[Translation] [fr]" in out


def test_render_tokens_handles_empty_input() -> None:
    assert render_tokens([], []) == ""


# ---------------------------------------------------------------------------
# start_audio_thread
# ---------------------------------------------------------------------------


def test_start_audio_thread_calls_send_bytes_and_exits() -> None:
    class _FakeSession:
        def __init__(self) -> None:
            self.received: list[bytes | object] = []

        def send_bytes(self, chunks: object) -> None:
            self.received.append(chunks)

    session = _FakeSession()
    thread = start_audio_thread(session, b"audio-data", name="t-test")  # type: ignore[arg-type]
    thread.join(timeout=2)
    assert not thread.is_alive()
    assert session.received == [b"audio-data"]


def test_start_audio_thread_returns_daemon_thread_with_given_name() -> None:
    class _FakeSession:
        def send_bytes(self, chunks: object) -> None:
            pass

    thread = start_audio_thread(
        _FakeSession(),  # type: ignore[arg-type]
        b"x",
        name="my-thread",
        daemon=True,
    )
    thread.join(timeout=1)
    assert thread.name == "my-thread"
    assert thread.daemon is True


def test_start_audio_thread_runs_in_background_not_caller() -> None:
    """The caller must not block on ``send_bytes`` - the work happens on the thread."""

    main_thread_id = threading.get_ident()
    captured: dict[str, int] = {}

    class _FakeSession:
        def send_bytes(self, chunks: object) -> None:
            captured["tid"] = threading.get_ident()
            time.sleep(0.01)

    session = _FakeSession()
    thread = start_audio_thread(session, b"x")  # type: ignore[arg-type]
    thread.join(timeout=2)
    assert captured["tid"] != main_thread_id


# ---------------------------------------------------------------------------
# output_file_for_audio_format
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "audio_format, expected_ext",
    [
        ("wav", "wav"),
        ("mp3", "mp3"),
        ("aac", "aac"),
        ("opus", "opus"),
        ("flac", "flac"),
        ("pcm_s16le", "pcm"),
        ("pcm_f32le", "pcm"),
        ("pcm_mulaw", "pcm"),
        ("pcm_alaw", "pcm"),
        ("unknown_format", "bin"),
    ],
)
def test_output_file_for_audio_format_picks_extension(
    audio_format: str, expected_ext: str
) -> None:
    path = output_file_for_audio_format(audio_format, "output")
    assert path == Path(f"output.{expected_ext}")


# ---------------------------------------------------------------------------
# start_text_thread
# ---------------------------------------------------------------------------


def test_start_text_thread_calls_send_text_chunks_and_exits() -> None:
    class _FakeSession:
        def __init__(self) -> None:
            self.received: list[str | object] = []
            self.text_end: bool | None = None

        def send_text_chunks(self, chunks: object, *, text_end: bool = True) -> None:
            self.received.append(chunks)
            self.text_end = text_end

    session = _FakeSession()
    thread = start_text_thread(session, "hello world", name="t-text", text_end=False)  # type: ignore[arg-type]
    thread.join(timeout=2)
    assert not thread.is_alive()
    assert session.received == ["hello world"]
    assert session.text_end is False


def test_start_text_thread_runs_in_background_not_caller() -> None:
    main_thread_id = threading.get_ident()
    captured: dict[str, int] = {}

    class _FakeSession:
        def send_text_chunks(self, chunks: object, *, text_end: bool = True) -> None:
            captured["tid"] = threading.get_ident()
            time.sleep(0.01)

    thread = start_text_thread(_FakeSession(), "x")  # type: ignore[arg-type]
    thread.join(timeout=2)
    assert captured["tid"] != main_thread_id
