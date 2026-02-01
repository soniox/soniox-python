from __future__ import annotations

import asyncio
import threading
import time
from collections.abc import AsyncIterator, Iterable, Iterator
from pathlib import Path
from typing import TYPE_CHECKING, BinaryIO

from soniox.realtime.stt import RealtimeSTTSession

from .types import Token

if TYPE_CHECKING:
    from soniox.realtime.async_stt import AsyncRealtimeSTTSession


def stream_audio(
    file: Path | str | BinaryIO | bytes,
    *,
    chunk_size_bytes: int = 4 * 1024,
) -> Iterator[bytes]:
    if chunk_size_bytes <= 0:
        raise ValueError("chunk_size_bytes must be greater than zero")

    if isinstance(file, bytes):
        data = bytes(file)
        for offset in range(0, len(data), chunk_size_bytes):
            yield data[offset : offset + chunk_size_bytes]
        return

    path_candidate = Path(file) if isinstance(file, str) else file
    if isinstance(path_candidate, Path):
        with path_candidate.open("rb") as handle:
            yield from _iter_chunks(handle, chunk_size_bytes)
        return

    assert isinstance(file, BinaryIO)
    yield from _iter_chunks(file, chunk_size_bytes)


async def stream_audio_async(
    file: Path | str | BinaryIO | bytes,
    *,
    chunk_size_bytes: int = 4 * 1024,
) -> AsyncIterator[bytes]:
    if chunk_size_bytes <= 0:
        raise ValueError("chunk_size_bytes must be greater than zero")

    if isinstance(file, bytes):
        data = bytes(file)
        for offset in range(0, len(data), chunk_size_bytes):
            yield data[offset : offset + chunk_size_bytes]
        return

    path_candidate = Path(file) if isinstance(file, str) else file
    if isinstance(path_candidate, Path):
        with path_candidate.open("rb") as handle:
            async for chunk in _async_iter_chunks(handle, chunk_size_bytes):
                yield chunk
        return

    assert isinstance(file, BinaryIO)
    async for chunk in _async_iter_chunks(file, chunk_size_bytes):
        yield chunk


async def _async_iter_chunks(handle: BinaryIO, chunk_size: int) -> AsyncIterator[bytes]:
    loop = asyncio.get_running_loop()
    while chunk := await loop.run_in_executor(None, handle.read, chunk_size):
        yield chunk


def _iter_chunks(handle: BinaryIO, chunk_size: int) -> Iterable[bytes]:
    while chunk := handle.read(chunk_size):
        yield chunk


def throttle_audio(
    file: Path | str | BinaryIO | bytes,
    *,
    chunk_size_bytes: int = 4096,
    delay_seconds: float = 0.0,
) -> Iterator[bytes]:
    if delay_seconds < 0:
        raise ValueError("delay_seconds must be greater than or equal to zero")

    for chunk in stream_audio(file, chunk_size_bytes=chunk_size_bytes):
        yield chunk
        if delay_seconds:
            time.sleep(delay_seconds)


async def throttle_audio_async(
    file: Path | str | BinaryIO | bytes,
    *,
    chunk_size_bytes: int = 32 * 1024,
    delay_seconds: float = 0.0,
) -> AsyncIterator[bytes]:
    if delay_seconds < 0:
        raise ValueError("delay_seconds must be greater than or equal to zero")

    async for chunk in stream_audio_async(file, chunk_size_bytes=chunk_size_bytes):
        yield chunk
        if delay_seconds:
            await asyncio.sleep(delay_seconds)


def render_tokens(final_tokens: list[Token], non_final_tokens: list[Token]) -> str:
    """Build a human-friendly transcript from token metadata."""
    text_parts: list[str] = []
    current_speaker: str | None = None
    current_language: str | None = None

    for token in final_tokens + non_final_tokens:
        text = token.text or ""
        speaker = token.speaker
        language = token.language
        is_translation = token.translation_status == "translation"

        if speaker is not None and speaker != current_speaker:
            if current_speaker is not None:
                text_parts.append("\n\n")
            current_speaker = speaker
            current_language = None
            text_parts.append(f"Speaker {current_speaker}:")

        if language is not None and language != current_language:
            current_language = language
            prefix = "[Translation] " if is_translation else ""
            text_parts.append(f"\n{prefix}[{current_language}] ")
            text = text.lstrip()

        text_parts.append(text)

    return "".join(text_parts)


def start_audio_thread(
    session: RealtimeSTTSession,
    chunks: bytes | Iterator[bytes],
    *,
    name: str | None = None,
    daemon: bool = True,
) -> threading.Thread:
    def _stream() -> None:
        session.send_bytes(chunks)

    thread = threading.Thread(target=_stream, daemon=daemon, name=name)
    thread.start()
    return thread


def start_keep_alive_thread(
    session: RealtimeSTTSession,
    *,
    interval_seconds: float = 10.0,
    name: str | None = None,
    daemon: bool = True,
) -> tuple[threading.Thread, threading.Event]:
    if not 1.0 <= interval_seconds <= 20.0:
        raise ValueError("interval_seconds must be between 1 and 20 seconds")

    stop_event = threading.Event()

    def _keep_alive() -> None:
        while not stop_event.is_set():
            time.sleep(interval_seconds)
            if stop_event.is_set():
                break
            session.send_keep_alive()

    thread = threading.Thread(target=_keep_alive, daemon=daemon, name=name)
    thread.start()
    return thread, stop_event


async def keep_alive_async(
    session: "AsyncRealtimeSTTSession",
    *,
    interval_seconds: float = 10.0,
    stop_event: asyncio.Event | None = None,
) -> None:
    if not 1.0 <= interval_seconds <= 20.0:
        raise ValueError("interval_seconds must be between 1 and 20 seconds")

    if stop_event is None:
        stop_event = asyncio.Event()

    while not stop_event.is_set():
        await asyncio.sleep(interval_seconds)
        if stop_event.is_set():
            break
        await session.send_keep_alive()
