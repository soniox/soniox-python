from __future__ import annotations

import asyncio
import os
from pathlib import Path
from textwrap import indent

from soniox import AsyncSonioxClient
from soniox.types.api import TranslationConfig
from soniox.types.realtime import RealtimeEvent, RealtimeSttConfig
from soniox.utils import (
    render_tokens,
    stream_audio_file_async,
    translation_transcript_segments,
)

MODEL_ID = "stt-rt-v3"
ASSET_NAME = "audio_short.mp3"


def _assets_dir() -> Path:
    return Path(__file__).resolve().parents[1] / "assets"


def _print_event(event: RealtimeEvent, label: str) -> None:
    print(f"\n(async) {label} event (finished={event.finished}, error={event.error_code}):")
    for token in event.tokens[:4]:
        print(
            indent(
                f"{token.text!r} [{token.language}] speaker={token.speaker} translation={token.translation_status}",
                "  ",
            )
        )
    if event.tokens:
        token_dicts = [token.model_dump() for token in event.tokens]
        print("\n(async) Rendered event tokens:")
        print(indent(render_tokens(token_dicts), "  "))
        for segment in translation_transcript_segments(token_dicts):
            label = "translation" if segment.is_translation else "source"
            lang = segment.language or "unknown"
            print(f"  [{label} | {lang}] {segment.text.strip()}")


async def main() -> None:
    api_key = os.environ.get("SONIOX_API_KEY")
    if not api_key:
        raise SystemExit("Please set SONIOX_API_KEY to run the async realtime example.")

    audio_path = _assets_dir() / ASSET_NAME

    async with AsyncSonioxClient(api_key=api_key) as client:
        config = RealtimeSttConfig(
            model=MODEL_ID,
            audio_format="auto",
            translation=TranslationConfig(type="one_way", target_language="es"),
        )
        async with client.realtime.stt.connect(config=config) as session:
            print("Streaming audio to realtime session (async)...")
            await session.stream_audio(stream_audio_file_async(audio_path))
            final_event: RealtimeEvent | None = None
            async for event in session.receive_events():
                final_event = event
                _print_event(event, "Realtime")
                if event.error_code:
                    print(f"Realtime error {event.error_code}: {event.error_message}")
                    break
                if event.finished:
                    break
            if final_event is None:
                print("\n(async) Realtime session completed without receiving events.")
            elif final_event.error_code:
                print(f"\n(async) Realtime session ended with error {final_event.error_code}.")
            else:
                print("\n(async) Realtime session completed successfully.")


if __name__ == "__main__":
    asyncio.run(main())
