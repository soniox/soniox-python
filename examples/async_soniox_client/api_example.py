import asyncio
from pathlib import Path

from soniox.client import AsyncSonioxClient
from soniox.errors import SonioxAPIError, SonioxNotFoundError

DEMO_FILE = Path(__file__).resolve().parents[2] / "assets" / "coffee_shop.mp3"


async def _print_uploads(client: AsyncSonioxClient) -> None:
    """Show a few recent uploads so developers understand the list endpoint."""
    page = await client.files.list(limit=3)
    print("Recent uploads (async):")
    for file in page.files:
        print(f"  - {file.filename} (id={file.id})")


async def _probe_missing_file(client: AsyncSonioxClient) -> None:
    """Intentionally request a missing file to demonstrate SonioxNotFoundError."""
    missing_id = "non-existent-file"
    try:
        await client.files.get(missing_id)
    except SonioxNotFoundError:
        print(f"File {missing_id} is correctly reported as missing.")


async def main() -> None:
    client = AsyncSonioxClient()
    uploaded_id: str | None = None
    transcription_id: str | None = None
    try:
        await _print_uploads(client)
        await _probe_missing_file(client)

        uploaded = await client.files.upload(
            DEMO_FILE,
            client_reference_id="examples-async-simple",
        )
        uploaded_id = uploaded.id
        print(f"Uploaded {uploaded.filename} (id={uploaded.id})")

        transcription = await client.stt.create(file_id=uploaded.id)
        transcription_id = transcription.id
        print("Polling transcription until completion...")
        finished = await client.stt.wait(transcription.id, timeout_sec=60)
        print(f"Status: {finished.status}")

        transcript = await client.stt.get_transcript(transcription.id)
        print("Transcript snippet:")
        print(transcript.text[:200].strip() or "<no text yet>")

    except SonioxAPIError as exc:
        print("Soniox API error:", exc)
        if exc.request_id:
            print("  request_id:", exc.request_id)
    finally:
        if transcription_id:
            await client.stt.delete(transcription_id)
            print(f"Deleted transcription {transcription_id}")
        if uploaded_id:
            await client.files.delete(uploaded_id)
            print(f"Deleted temporary upload {uploaded_id}")
        await client.aclose()


asyncio.run(main())
