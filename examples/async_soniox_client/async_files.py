from __future__ import annotations

import asyncio
import os
from pathlib import Path
from textwrap import indent

from soniox import AsyncSonioxClient

ASSET_NAME = "audio_short.mp3"


def _assets_dir() -> Path:
    return Path(__file__).resolve().parents[1] / "assets"


def _env_flag(name: str) -> bool:
    return os.environ.get(name, "").strip().lower() in {"1", "true", "yes"}


async def _print_files_page(client: AsyncSonioxClient, limit: int = 3) -> None:
    page = await client.files.list(limit=limit)
    print(f"\n(async) Found {len(page.files)} recent file(s):")
    for stored in page.files:
        print(f" - {stored.id}: {stored.filename} ({stored.size} bytes)")


async def _show_file(client: AsyncSonioxClient, file_id: str) -> None:
    metadata = await client.files.get(file_id)
    print("\n(async) File metadata:")
    print(indent(f"id: {metadata.id}", "  "))
    print(indent(f"filename: {metadata.filename}", "  "))
    print(indent(f"size: {metadata.size}", "  "))
    print(indent(f"created_at: {metadata.created_at}", "  "))


async def _delete_file_if_requested(client: AsyncSonioxClient, file_id: str) -> None:
    if _env_flag("SONIOX_EXAMPLE_DELETE_FILE"):
        await client.files.delete(file_id)
        print(f"\n(async) Deleted file {file_id} (SONIOX_EXAMPLE_DELETE_FILE enabled)")
    else:
        print(f"\n(async) Leaving uploaded file {file_id} intact (set SONIOX_EXAMPLE_DELETE_FILE=1 to delete it)")


async def _optional_delete_all(client: AsyncSonioxClient) -> None:
    if _env_flag("SONIOX_EXAMPLE_DELETE_ALL_FILES"):
        await client.files.delete_all(limit=5)
        print("\n(async) Called client.files.delete_all(limit=5)")
    else:
        print("\n(async) Skipping delete_all (set SONIOX_EXAMPLE_DELETE_ALL_FILES=1 to run)")


async def main() -> None:
    api_key = os.environ.get("SONIOX_API_KEY")
    if not api_key:
        raise SystemExit("Please set SONIOX_API_KEY to run the async files example.")

    async with AsyncSonioxClient(api_key=api_key) as client:
        await _print_files_page(client)

        audio_path = _assets_dir() / ASSET_NAME
        print(f"\n(async) Uploading {audio_path.name!r}")
        upload = await client.files.upload(
            audio_path,
            client_reference_id="async-example-files",
        )
        print(f"(async) Uploaded {upload.id} ({upload.filename})")

        await _show_file(client, upload.id)
        await _delete_file_if_requested(client, upload.id)
        await _optional_delete_all(client)


if __name__ == "__main__":
    asyncio.run(main())
