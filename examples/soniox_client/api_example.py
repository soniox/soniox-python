from pathlib import Path

from soniox.client import SonioxClient
from soniox.errors import SonioxAPIError, SonioxNotFoundError

DEMO_FILE = Path(__file__).resolve().parents[2] / "assets" / "coffee_shop.mp3"


def _print_uploads(client: SonioxClient) -> None:
    """Show a few recent uploads so beginners understand the list call."""
    page = client.files.list(limit=3)
    print("Recent uploads (sync):")
    for file in page.files:
        print(f"  - {file.filename} (id={file.id})")


def _probe_missing_file(client: SonioxClient) -> None:
    """Fetch a fake ID to demonstrate `SonioxNotFoundError`."""
    missing_id = "non-existent-file"
    try:
        client.files.get(missing_id)
    except SonioxNotFoundError:
        print(f"File {missing_id} is correctly reported as missing.")


def main() -> None:
    client = SonioxClient()
    uploaded_id: str | None = None
    transcription_id: str | None = None
    try:
        _print_uploads(client)
        _probe_missing_file(client)

        uploaded = client.files.upload(
            DEMO_FILE,
            client_reference_id="examples-sync-simple",
        )
        uploaded_id = uploaded.id
        print(f"Uploaded {uploaded.filename} (id={uploaded.id})")

        transcription = client.stt.create(file_id=uploaded.id)
        transcription_id = transcription.id
        print("Polling transcription until completion...")
        finished = client.stt.wait(transcription.id, timeout_sec=60)
        print(f"Status: {finished.status}")

        transcript = client.stt.get_transcript(transcription.id)
        print("Transcript snippet:")
        print(transcript.text[:200].strip() or "<no text yet>")

    except SonioxAPIError as exc:
        print("Soniox API error:", exc)
        if exc.request_id:
            print("  request_id:", exc.request_id)
    finally:
        if transcription_id:
            client.stt.delete(transcription_id)
            print(f"Deleted transcription {transcription_id}")
        if uploaded_id:
            client.files.delete(uploaded_id)
            print(f"Deleted temporary upload {uploaded_id}")
        client.close()


main()
