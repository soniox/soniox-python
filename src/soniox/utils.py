from __future__ import annotations

import asyncio
import threading
import time
from collections.abc import AsyncIterator, Iterable, Iterator
from pathlib import Path
from typing import BinaryIO

from soniox.realtime.stt import RealtimeSTTSession

from .types import Token


def stream_audio(
    file: Path | str | BinaryIO | bytes,
    *,
    chunk_size_bytes: int = 4 * 1024,
) -> Iterator[bytes]:
    """
    Yield fixed-size chunks from an audio source.

    Supports bytes, file paths, or binary streams and slices them into
    `chunk_size_bytes` blocks for realtime transmission.
    """
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
    """
    Asynchronously yield fixed-size chunks from an audio source.

    Mirrors `stream_audio` but produces an async iterator for later consumption.
    """
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
    """Asynchronously read a binary stream in fixed-size chunks."""
    loop = asyncio.get_running_loop()
    while chunk := await loop.run_in_executor(None, handle.read, chunk_size):
        yield chunk


def _iter_chunks(handle: BinaryIO, chunk_size: int) -> Iterable[bytes]:
    """Synchronously read a binary stream in fixed-size chunks."""
    while chunk := handle.read(chunk_size):
        yield chunk


def throttle_audio(
    file: Path | str | BinaryIO | bytes,
    *,
    chunk_size_bytes: int = 4096,
    delay_seconds: float = 0.0,
) -> Iterator[bytes]:
    """
    Yield audio chunks at a regulated pace, optionally sleeping between yields.
    """
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
    """Async counterpart of `throttle_audio`, yielding chunks with optional delay."""
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
    """Stream audio into the session on a background thread."""

    def _stream() -> None:
        session.send_bytes(chunks)

    thread = threading.Thread(target=_stream, daemon=daemon, name=name)
    thread.start()
    return thread
