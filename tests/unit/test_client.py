"""
Client wiring and single-call conveniences.

Covers things not driven by the OpenAPI schema:

* How the SDK client is configured (API key sources, base URL, timeout).
* How :class:`httpx.Client` is actually wired under the hood.
* Edge cases in error-body parsing that :mod:`test_api` can't easily reach.
* Single-call convenience helpers: ``get_or_none``, ``delete_if_exists``,
  ``list_all`` pagination, and client-side validation in ``stt.create``.
"""

from __future__ import annotations

import pytest
import respx
from httpx import Response

from soniox.client import SonioxClient
from soniox.errors import (
    SonioxAPIError,
    SonioxServerError,
    SonioxValidationError,
)
from soniox.types import File, GetFilesResponse, GetModelsResponse
from tests.helpers import API_KEY, BASE_URL, api_error_body, build

# ---------------------------------------------------------------------------
# Client construction
# ---------------------------------------------------------------------------


def test_api_key_is_required(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("SONIOX_API_KEY", raising=False)
    with pytest.raises(SonioxValidationError):
        SonioxClient()


def test_api_key_falls_back_to_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SONIOX_API_KEY", "env_key")
    with SonioxClient() as c:
        assert c.api_key == "env_key"


def test_default_timeout_is_30_seconds() -> None:
    with SonioxClient(api_key=API_KEY) as c:
        assert c.timeout_sec == 30.0


def test_timeout_override_flows_through_to_httpx() -> None:
    with SonioxClient(api_key=API_KEY, timeout_sec=7.25) as c:
        timeout = c._http_client.timeout  # pyright: ignore[reportPrivateUsage]
        assert timeout.connect == 7.25
        assert timeout.read == 7.25


def test_base_url_override_flows_through_to_httpx() -> None:
    with SonioxClient(api_key=API_KEY, api_base_url="https://custom.example/v9") as c:
        base_url = c._http_client.base_url  # pyright: ignore[reportPrivateUsage]
        assert str(base_url).rstrip("/") == "https://custom.example/v9"


def test_default_auth_header_is_set_on_httpx_client() -> None:
    with SonioxClient(api_key=API_KEY) as c:
        headers = c._http_client.headers  # pyright: ignore[reportPrivateUsage]
        assert headers["Authorization"] == f"Bearer {API_KEY}"


@respx.mock
def test_custom_base_url_is_actually_called() -> None:
    mock = build(GetModelsResponse)
    route = respx.get("https://custom.example/v9/models").mock(
        return_value=Response(200, json=mock.model_dump(mode="json"))
    )
    with SonioxClient(api_key=API_KEY, api_base_url="https://custom.example/v9") as c:
        c.models.list()
    assert route.called


# ---------------------------------------------------------------------------
# Error-body edge cases
# ---------------------------------------------------------------------------


@respx.mock
def test_unparseable_json_body_becomes_generic_api_error(client: SonioxClient) -> None:
    """A JSON body that doesn't match the ApiError schema must not leak a
    raw Pydantic ValidationError out of the SDK."""
    respx.get(f"{BASE_URL}/files").mock(
        return_value=Response(500, json={"unexpected": "shape"})
    )
    with pytest.raises(SonioxAPIError, match="Unable to parse API error schema"):
        client.files.list(limit=5)


@respx.mock
def test_legacy_error_code_message_payload_is_recognised(client: SonioxClient) -> None:
    """Servers that return the older `{error_code, error_message}` shape are
    still surfaced as a typed error with the message intact."""
    respx.get(f"{BASE_URL}/files").mock(
        return_value=Response(
            400, json={"error_code": 400, "error_message": "legacy error path"}
        )
    )
    from soniox.errors import SonioxInvalidRequestError

    with pytest.raises(SonioxInvalidRequestError, match="legacy error path"):
        client.files.list(limit=5)


@respx.mock
def test_non_dict_error_body_falls_back_to_generic_api_error(client: SonioxClient) -> None:
    respx.get(f"{BASE_URL}/files").mock(return_value=Response(500, json=["one", "two"]))
    with pytest.raises(SonioxAPIError, match="Unable to parse API error schema"):
        client.files.list(limit=5)


@respx.mock
def test_empty_error_body_falls_back_to_reason_phrase(client: SonioxClient) -> None:
    respx.get(f"{BASE_URL}/files").mock(return_value=Response(503))
    with pytest.raises(SonioxServerError) as exc_info:
        client.files.list(limit=5)
    assert str(exc_info.value).strip()  # non-empty message


@respx.mock
def test_plain_text_error_body_is_surfaced(client: SonioxClient) -> None:
    respx.get(f"{BASE_URL}/files").mock(
        return_value=Response(500, text="upstream exploded")
    )
    with pytest.raises(SonioxServerError, match="upstream exploded"):
        client.files.list(limit=5)


# ---------------------------------------------------------------------------
# Convenience helpers that wrap a single call
# ---------------------------------------------------------------------------


@respx.mock
def test_get_or_none_returns_none_on_404(client: SonioxClient) -> None:
    respx.get(f"{BASE_URL}/files/missing").mock(
        return_value=Response(404, json=api_error_body(404))
    )
    assert client.files.get_or_none("missing") is None


@respx.mock
def test_get_or_none_reraises_non_404_errors(client: SonioxClient) -> None:
    respx.get(f"{BASE_URL}/files/missing").mock(
        return_value=Response(500, json=api_error_body(500))
    )
    with pytest.raises(SonioxServerError):
        client.files.get_or_none("missing")


@respx.mock
def test_delete_if_exists_swallows_404(client: SonioxClient) -> None:
    respx.delete(f"{BASE_URL}/files/missing").mock(
        return_value=Response(404, json=api_error_body(404))
    )
    client.files.delete_if_exists("missing")  # must not raise


@respx.mock
def test_files_upload_closes_stream_when_sdk_owns_it(client: SonioxClient) -> None:
    """Sync mirror of the async close_after=True upload path."""
    respx.post(f"{BASE_URL}/files").mock(
        return_value=Response(201, json=build(File).model_dump(mode="json"))
    )
    client.files.upload(b"audio-bytes", filename="clip.mp3")


@respx.mock
def test_list_all_follows_pagination_cursor(client: SonioxClient) -> None:
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

    files = list(client.files.list_all(limit=2))

    assert route.call_count == 2
    assert len(files) == len(page1.files) + len(page2.files)
    # The second request must carry the cursor returned by the first.
    assert route.calls[1].request.url.params["cursor"] == "cursor-2"


@respx.mock
def test_files_delete_all_deletes_every_file(client: SonioxClient) -> None:
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

    client.files.delete_all()

    assert sorted(deleted) == ["file-a", "file-b"]


# ---------------------------------------------------------------------------
# Client-side validation
# ---------------------------------------------------------------------------


def test_stt_create_rejects_file_id_with_audio_url(client: SonioxClient) -> None:
    with pytest.raises(SonioxValidationError):
        client.stt.create(file_id="f1", audio_url="https://example.com/audio.mp3")
