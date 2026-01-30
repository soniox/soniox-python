from __future__ import annotations

import asyncio
import os
from pathlib import Path
from textwrap import indent

from soniox import AsyncSonioxClient
from soniox.types.api import CreateTranscriptionPayload, TranscriptionTranscript
from soniox.types.webhooks import WebhookAuthConfig
from soniox.utils import render_tokens, translation_transcript_segments

MODEL_ID = "stt-async-v3"
ASSET_NAME = "audio_short.mp3"
EXAMPLE_AUDIO_URL = "https://soniox.com/media/examples/coffee_shop.mp3"


def _assets_dir() -> Path:
    return Path(__file__).resolve().parents[1] / "assets"


def _env_flag(name: str) -> bool:
    return os.environ.get(name, "").strip().lower() in {"1", "true", "yes"}


def _print_translation_segments(tokens: list[dict[str, object]]) -> None:
    print("\n(async) Token segments (source/translation):")
    for segment in translation_transcript_segments(tokens):
        label = "translation" if segment.is_translation else "source"
        lang = segment.language or "unknown"
        print(f"  [{label} | {lang}] {segment.text.strip()}")


def _print_transcript(transcript: TranscriptionTranscript) -> None:
    print("\n(async) Transcript text:")
    print(indent(transcript.text, "  "))
    token_dicts = [token.model_dump() for token in transcript.tokens]
    print("\n(async) Rendered transcript preview:")
    print(indent(render_tokens(token_dicts), "  "))
    _print_translation_segments(token_dicts)


async def main() -> None:
    api_key = os.environ.get("SONIOX_API_KEY")
    if not api_key:
        raise SystemExit("Please set SONIOX_API_KEY to run the async transcriptions example.")

    async with AsyncSonioxClient(api_key=api_key) as client:
        page = await client.transcriptions.list(limit=3)
        print(f"(async) Listing {len(page.transcriptions)} recent transcription(s):")
        for transcription in page.transcriptions:
            print(f" - {transcription.id}: {transcription.status}")

        audio_path = _assets_dir() / ASSET_NAME
        delete_after = _env_flag("SONIOX_EXAMPLE_DELETE_AFTER")
        transcription = await client.transcriptions.transcribe_and_wait(
            model=MODEL_ID,
            file=audio_path,
            wait=True,
            language_hints=["en"],
            delete_after=delete_after,
        )
        print(
            f"\n(async) Submitted transcription {transcription.id} (status: {transcription.status})"
        )

        if delete_after:
            print(
                "\n(async) delete_after is enabled, so the transcription (and linked file) were removed."
                " Transcript retrieval is skipped."
            )
            print(
                "\n(async) Additional transcription workflows are skipped because delete_after removed the transcription."
            )
        else:
            fetched = await client.transcriptions.get(transcription.id)
            print(f"\n(async) Retrieved transcription {fetched.id} (status: {fetched.status})")

            transcript = await client.transcriptions.get_transcript(transcription.id)
            _print_transcript(transcript)

            if _env_flag("SONIOX_EXAMPLE_TRANSCRIBE_URL"):
                url_transcription = await client.transcriptions.transcribe_from_url(
                    model=MODEL_ID,
                    audio_url=EXAMPLE_AUDIO_URL,
                )
                print(
                    f"\n(async) Submitted URL transcription {url_transcription.id} (status: {url_transcription.status})"
                )

            if _env_flag("SONIOX_EXAMPLE_CREATE_PAYLOAD"):
                payload = CreateTranscriptionPayload(model=MODEL_ID, audio_url=EXAMPLE_AUDIO_URL)
                manual = await client.transcriptions.create(payload)
                print(f"\n(async) Created transcription {manual.id} via client.transcriptions.create()")

            if _env_flag("SONIOX_EXAMPLE_FILE_ID"):
                upload = await client.files.upload(
                    audio_path, client_reference_id="async-example-transcribe-fileid"
                )
                file_id_transcription = await client.transcriptions.transcribe_from_file_id(
                    model=MODEL_ID,
                    file_id=upload.id,
                    client_reference_id="async-example-transcription-fileid",
                )
                print(f"\n(async) Submitted transcription {file_id_transcription.id} via file_id")

            if _env_flag("SONIOX_EXAMPLE_WEBHOOK"):
                webhook_transcription = await client.transcriptions.transcribe_file_with_webhook(
                    model=MODEL_ID,
                    file=audio_path,
                    webhook_url="https://example.com/soniox",
                    webhook_auth=WebhookAuthConfig(name="Authorization", value="Bearer secret"),
                )
                print(f"\n(async) Submitted webhook transcription {webhook_transcription.id}")

            if _env_flag("SONIOX_EXAMPLE_DELETE_TRANSCRIPTION"):
                await client.transcriptions.delete(transcription.id)
                print(f"\n(async) Deleted transcription {transcription.id}")
            elif _env_flag("SONIOX_EXAMPLE_DESTROY_TRANSCRIPTION"):
                await client.transcriptions.destroy(transcription.id)
                print(f"\n(async) Destroyed transcription {transcription.id} and linked file")
            else:
                print(
                    "\n(async) Keeping transcription available (set SONIOX_EXAMPLE_DELETE_TRANSCRIPTION=1 to delete it)"
                )


if __name__ == "__main__":
    asyncio.run(main())
