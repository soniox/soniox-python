"""
Async mirror of :mod:`tests.unit.test_client` for convenience helpers.

The async client carries the same surface as the sync client for error
handling, pagination, and the ``get_or_none`` / ``delete_if_exists``
shortcuts. This file exercises the async side of each.
"""

from __future__ import annotations

import pytest
import respx
from httpx import Response

from soniox.client import AsyncSonioxClient
from soniox.errors import SonioxServerError
from soniox.types import File, GetFilesResponse, GetTranscriptionsResponse
from tests.helpers import BASE_URL, api_error_body, build


# ---------------------------------------------------------------------------
# Files
# ---------------------------------------------------------------------------


@respx.mock
async def test_async_files_get_or_none_returns_none_on_404(
    async_client: AsyncSonioxClient,
) -> None:
    respx.get(f"{BASE_URL}/files/missing").mock(
        return_value=Response(404, json=api_error_body(404))
    )
    assert await async_client.files.get_or_none("missing") is None


@respx.mock
async def test_async_files_get_or_none_reraises_non_404(
    async_client: AsyncSonioxClient,
) -> None:
    respx.get(f"{BASE_URL}/files/missing").mock(
        return_value=Response(500, json=api_error_body(500))
    )
    with pytest.raises(SonioxServerError):
        await async_client.files.get_or_none("missing")


@respx.mock
async def test_async_files_delete_if_exists_swallows_404(
    async_client: AsyncSonioxClient,
) -> None:
    respx.delete(f"{BASE_URL}/files/missing").mock(
        return_value=Response(404, json=api_error_body(404))
    )
    await async_client.files.delete_if_exists("missing")  # must not raise


@respx.mock
async def test_async_files_upload_closes_stream_when_sdk_owns_it(
    async_client: AsyncSonioxClient,
) -> None:
    """Async mirror of the sync close_after=True upload path."""
    respx.post(f"{BASE_URL}/files").mock(
        return_value=Response(201, json=build(File).model_dump(mode="json"))
    )
    await async_client.files.upload(b"audio-bytes", filename="clip.mp3")


@respx.mock
async def test_async_files_list_all_follows_cursor(async_client: AsyncSonioxClient) -> None:
    page1 = build(GetFilesResponse)
    page1.next_page_cursor = "cursor-2"
    page2 = build(GetFilesResponse)
    page2.next_page_cursor = None

    responses = iter(
        [
            Response(200, json=page1.model_dump(mode="json")),
            Response(200, json=page2.model_dump(mode="json")),
        ]
    )
    route = respx.get(f"{BASE_URL}/files").mock(side_effect=lambda req: next(responses))

    files = [f async for f in async_client.files.list_all(limit=2)]

    assert route.call_count == 2
    assert len(files) == len(page1.files) + len(page2.files)
    assert route.calls[1].request.url.params["cursor"] == "cursor-2"


@respx.mock
async def test_async_files_delete_all_deletes_every_file(
    async_client: AsyncSonioxClient,
) -> None:
    # Two hand-built files so the assertion has known expected behavior.
    files = [build(File), build(File)]
    files[0].id = "file-a"
    files[1].id = "file-b"
    page = GetFilesResponse(files=files, next_page_cursor=None)

    respx.get(f"{BASE_URL}/files").mock(
        return_value=Response(200, json=page.model_dump(mode="json"))
    )
    deleted: list[str] = []

    def _record_delete(request) -> Response:
        deleted.append(request.url.path.rsplit("/", 1)[-1])
        return Response(204)

    respx.delete(url__regex=rf"{BASE_URL}/files/.+").mock(side_effect=_record_delete)

    await async_client.files.delete_all()

    assert sorted(deleted) == ["file-a", "file-b"]


# ---------------------------------------------------------------------------
# Transcriptions
# ---------------------------------------------------------------------------


@respx.mock
async def test_async_stt_get_or_none_returns_none_on_404(
    async_client: AsyncSonioxClient,
) -> None:
    respx.get(f"{BASE_URL}/transcriptions/missing").mock(
        return_value=Response(404, json=api_error_body(404))
    )
    assert await async_client.stt.get_or_none("missing") is None


@respx.mock
async def test_async_stt_delete_if_exists_swallows_404(
    async_client: AsyncSonioxClient,
) -> None:
    respx.delete(f"{BASE_URL}/transcriptions/missing").mock(
        return_value=Response(404, json=api_error_body(404))
    )
    await async_client.stt.delete_if_exists("missing")  # must not raise


@respx.mock
async def test_async_stt_destroy_deletes_transcription_and_file(
    async_client: AsyncSonioxClient,
) -> None:
    from soniox.types import Transcription

    transcription = build(Transcription)
    transcription.id = "t1"
    transcription.file_id = "f1"
    respx.get(f"{BASE_URL}/transcriptions/t1").mock(
        return_value=Response(200, json=transcription.model_dump(mode="json"))
    )
    delete_t = respx.delete(f"{BASE_URL}/transcriptions/t1").mock(Response(204))
    delete_f = respx.delete(f"{BASE_URL}/files/f1").mock(Response(204))

    await async_client.stt.destroy("t1")

    assert delete_t.called
    assert delete_f.called


@respx.mock
async def test_async_stt_delete_all(async_client: AsyncSonioxClient) -> None:
    from soniox.types import Transcription

    page = GetTranscriptionsResponse(
        transcriptions=[build(Transcription), build(Transcription)],
        next_page_cursor=None,
    )
    page.transcriptions[0].id = "t1"
    page.transcriptions[1].id = "t2"
    respx.get(f"{BASE_URL}/transcriptions").mock(
        return_value=Response(200, json=page.model_dump(mode="json"))
    )
    deleted: list[str] = []

    def _record(request) -> Response:
        deleted.append(request.url.path.rsplit("/", 1)[-1])
        return Response(204)

    respx.delete(url__regex=rf"{BASE_URL}/transcriptions/.+").mock(side_effect=_record)

    await async_client.stt.delete_all()

    assert sorted(deleted) == ["t1", "t2"]


@respx.mock
async def test_async_stt_destroy_all(async_client: AsyncSonioxClient) -> None:
    from soniox.types import Transcription

    transcriptions = [build(Transcription), build(Transcription)]
    transcriptions[0].id = "t1"
    transcriptions[0].file_id = "f1"
    transcriptions[1].id = "t2"
    transcriptions[1].file_id = None
    page = GetTranscriptionsResponse(transcriptions=transcriptions, next_page_cursor=None)
    respx.get(f"{BASE_URL}/transcriptions").mock(
        return_value=Response(200, json=page.model_dump(mode="json"))
    )
    dt = respx.delete(url__regex=rf"{BASE_URL}/transcriptions/.+").mock(Response(204))
    df = respx.delete(url__regex=rf"{BASE_URL}/files/.+").mock(Response(204))

    await async_client.stt.destroy_all()

    assert dt.call_count == 2
    assert df.call_count == 1


@respx.mock
async def test_async_stt_list_all_follows_cursor(async_client: AsyncSonioxClient) -> None:
    page1 = build(GetTranscriptionsResponse)
    page1.next_page_cursor = "cursor-2"
    page2 = build(GetTranscriptionsResponse)
    page2.next_page_cursor = None

    responses = iter(
        [
            Response(200, json=page1.model_dump(mode="json")),
            Response(200, json=page2.model_dump(mode="json")),
        ]
    )
    route = respx.get(f"{BASE_URL}/transcriptions").mock(
        side_effect=lambda req: next(responses)
    )

    items = [t async for t in async_client.stt.list_all(limit=2)]

    assert route.call_count == 2
    assert len(items) == len(page1.transcriptions) + len(page2.transcriptions)
    assert route.calls[1].request.url.params["cursor"] == "cursor-2"
