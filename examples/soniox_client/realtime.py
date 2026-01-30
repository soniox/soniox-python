from __future__ import annotations

import os
from pathlib import Path
from textwrap import indent

from soniox import SonioxClient
from soniox.types.api import TranslationConfig
from soniox.types.realtime import RealtimeEvent, RealtimeSttConfig
from soniox.utils import render_tokens, stream_audio_file, translation_transcript_segments

MODEL_ID = "stt-rt-v3"
ASSET_NAME = "audio_short.mp3"


def _assets_dir() -> Path:
    return Path(__file__).resolve().parents[1] / "assets"


def _print_event(event: RealtimeEvent, label: str) -> None:
    print(f"\n{label} event (finished={event.finished}, error={event.error_code}):")
    for token in event.tokens[:4]:
        print(
            indent(
                f"{token.text!r} [{token.language}] speaker={token.speaker} translation={token.translation_status}",
                "  ",
            )
        )
    if event.tokens:
        token_dicts = [token.model_dump() for token in event.tokens]
        print("\nRendered event tokens:")
        print(indent(render_tokens(token_dicts), "  "))
        _print_translation_segments(token_dicts)


def _print_translation_segments(tokens: list[dict[str, object]]) -> None:
    for segment in translation_transcript_segments(tokens):
        label = "translation" if segment.is_translation else "source"
        lang = segment.language or "unknown"
        print(f"  [{label} | {lang}] {segment.text.strip()}")


def main() -> None:
    api_key = os.environ.get("SONIOX_API_KEY")
    if not api_key:
        raise SystemExit("Please set SONIOX_API_KEY to run the realtime example.")

    audio_path = _assets_dir() / ASSET_NAME

    with SonioxClient(api_key=api_key) as client:
        config = RealtimeSttConfig(
            model=MODEL_ID,
            audio_format="auto",
            translation=TranslationConfig(type="one_way", target_language="es"),
        )
        with client.realtime.stt.connect(config=config) as session:
            print("Streaming audio to realtime session...")
            session.stream_audio(stream_audio_file(audio_path))
            for event in session.receive_events():
                if event.error_code:
                    print(f"Realtime error {event.error_code}: {event.error_message}")
                    break
                _print_event(event, "Realtime")


if __name__ == "__main__":
    main()
