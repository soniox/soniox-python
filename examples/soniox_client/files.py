from __future__ import annotations

import os
from pathlib import Path
from textwrap import indent

from soniox import SonioxClient

ASSET_NAME = "audio_short.mp3"


def _assets_dir() -> Path:
    return Path(__file__).resolve().parents[1] / "assets"


def _env_flag(name: str) -> bool:
    return os.environ.get(name, "").strip().lower() in {"1", "true", "yes"}


def _print_files_page(client: SonioxClient, limit: int = 3) -> None:
    page = client.files.list(limit=limit)
    print(f"\nFound {len(page.files)} recent file(s):")
    for stored in page.files:
        print(f" - {stored.id}: {stored.filename} ({stored.size} bytes)")


def _show_file(client: SonioxClient, file_id: str) -> None:
    metadata = client.files.get(file_id)
    print("\nFile metadata:")
    print(indent(f"id: {metadata.id}", "  "))
    print(indent(f"filename: {metadata.filename}", "  "))
    print(indent(f"size: {metadata.size}", "  "))
    print(indent(f"created_at: {metadata.created_at}", "  "))


def _delete_file_if_requested(client: SonioxClient, file_id: str) -> None:
    if _env_flag("SONIOX_EXAMPLE_DELETE_FILE"):
        client.files.delete(file_id)
        print(f"\nDeleted file {file_id} (SONIOX_EXAMPLE_DELETE_FILE enabled)")
    else:
        print(f"\nLeaving uploaded file {file_id} intact (set SONIOX_EXAMPLE_DELETE_FILE=1 to delete it)")


def _optional_delete_all(client: SonioxClient) -> None:
    if _env_flag("SONIOX_EXAMPLE_DELETE_ALL_FILES"):
        client.files.delete_all(limit=5)
        print("\nCalled client.files.delete_all(limit=5)")
    else:
        print("\nSkipping delete_all (set SONIOX_EXAMPLE_DELETE_ALL_FILES=1 to run)")


def main() -> None:
    api_key = os.environ.get("SONIOX_API_KEY")
    if not api_key:
        raise SystemExit("Please set SONIOX_API_KEY to run the files example.")

    with SonioxClient(api_key=api_key) as client:
        _print_files_page(client)

        audio_path = _assets_dir() / ASSET_NAME
        print(f"\nUploading {audio_path.name!r}")
        upload = client.files.upload(
            audio_path,
            client_reference_id="example-files",
        )
        print(f"Uploaded {upload.id} ({upload.filename})")

        _show_file(client, upload.id)
        _delete_file_if_requested(client, upload.id)
        _optional_delete_all(client)


if __name__ == "__main__":
    main()
