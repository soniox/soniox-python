"""
Coverage for the less-used STT helpers: ``list_all`` pagination over
transcriptions, ``delete_all``, ``destroy`` (delete transcription + its file),
and ``destroy_all``.

Sync-side only - the async equivalents are exercised in
:mod:`tests.unit.test_async_client` and :mod:`tests.unit.test_async_stt_workflows`.
"""

from __future__ import annotations

import respx
from httpx import Response

from soniox.client import SonioxClient
from soniox.types import GetTranscriptionsResponse, Transcription
from tests.helpers import BASE_URL, build


def _transcription(tid: str, *, file_id: str | None = None) -> Transcription:
    t = build(Transcription)
    t.id = tid
    t.file_id = file_id
    return t


# ---------------------------------------------------------------------------
# list_all
# ---------------------------------------------------------------------------


@respx.mock
def test_stt_list_all_follows_cursor(client: SonioxClient) -> None:
    page1 = GetTranscriptionsResponse(
        transcriptions=[_transcription("t1")], next_page_cursor="cursor-2"
    )
    page2 = GetTranscriptionsResponse(
        transcriptions=[_transcription("t2")], next_page_cursor=None
    )
    responses = iter(
        [
            Response(200, json=page1.model_dump(mode="json")),
            Response(200, json=page2.model_dump(mode="json")),
        ]
    )
    route = respx.get(f"{BASE_URL}/transcriptions").mock(
        side_effect=lambda req: next(responses)
    )

    items = list(client.stt.list_all(limit=2))

    assert route.call_count == 2
    assert [t.id for t in items] == ["t1", "t2"]
    assert route.calls[1].request.url.params["cursor"] == "cursor-2"


# ---------------------------------------------------------------------------
# delete_all
# ---------------------------------------------------------------------------


@respx.mock
def test_stt_delete_all_deletes_every_transcription(client: SonioxClient) -> None:
    page = GetTranscriptionsResponse(
        transcriptions=[_transcription("t1"), _transcription("t2")],
        next_page_cursor=None,
    )
    respx.get(f"{BASE_URL}/transcriptions").mock(
        return_value=Response(200, json=page.model_dump(mode="json"))
    )
    deleted: list[str] = []

    def _record_delete(request) -> Response:
        deleted.append(request.url.path.rsplit("/", 1)[-1])
        return Response(204)

    respx.delete(url__regex=rf"{BASE_URL}/transcriptions/.+").mock(side_effect=_record_delete)

    client.stt.delete_all()

    assert sorted(deleted) == ["t1", "t2"]


# ---------------------------------------------------------------------------
# destroy - delete transcription + its source file
# ---------------------------------------------------------------------------


@respx.mock
def test_stt_destroy_deletes_transcription_and_file(client: SonioxClient) -> None:
    respx.get(f"{BASE_URL}/transcriptions/t1").mock(
        return_value=Response(200, json=_transcription("t1", file_id="f1").model_dump(mode="json"))
    )
    delete_t = respx.delete(f"{BASE_URL}/transcriptions/t1").mock(Response(204))
    delete_f = respx.delete(f"{BASE_URL}/files/f1").mock(Response(204))

    client.stt.destroy("t1")

    assert delete_t.called
    assert delete_f.called


@respx.mock
def test_stt_destroy_skips_file_delete_when_no_file_id(client: SonioxClient) -> None:
    respx.get(f"{BASE_URL}/transcriptions/t1").mock(
        return_value=Response(200, json=_transcription("t1", file_id=None).model_dump(mode="json"))
    )
    delete_t = respx.delete(f"{BASE_URL}/transcriptions/t1").mock(Response(204))

    client.stt.destroy("t1")

    assert delete_t.called


# ---------------------------------------------------------------------------
# destroy_all - list + destroy each
# ---------------------------------------------------------------------------


@respx.mock
def test_stt_destroy_all_deletes_transcriptions_and_files(client: SonioxClient) -> None:
    page = GetTranscriptionsResponse(
        transcriptions=[
            _transcription("t1", file_id="f1"),
            _transcription("t2", file_id=None),  # url-based; no file to clean up
            _transcription("t3", file_id="f3"),
        ],
        next_page_cursor=None,
    )
    respx.get(f"{BASE_URL}/transcriptions").mock(
        return_value=Response(200, json=page.model_dump(mode="json"))
    )

    deleted_transcriptions: list[str] = []
    deleted_files: list[str] = []

    def _del_t(req) -> Response:
        deleted_transcriptions.append(req.url.path.rsplit("/", 1)[-1])
        return Response(204)

    def _del_f(req) -> Response:
        deleted_files.append(req.url.path.rsplit("/", 1)[-1])
        return Response(204)

    respx.delete(url__regex=rf"{BASE_URL}/transcriptions/.+").mock(side_effect=_del_t)
    respx.delete(url__regex=rf"{BASE_URL}/files/.+").mock(side_effect=_del_f)

    client.stt.destroy_all()

    assert sorted(deleted_transcriptions) == ["t1", "t2", "t3"]
    assert sorted(deleted_files) == ["f1", "f3"]
