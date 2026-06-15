"""
Schema-driven REST API tests.

The endpoint list is derived at collection time from ``openapi.json`` and
paired with an SDK call from :mod:`tests.unit._sdk_bindings`. A coverage
guard enforces that every operation in the schema has a binding, so adding
a new endpoint to the API surfaces as a test failure here.
"""

from __future__ import annotations

import json
from typing import Any

import httpx
import pytest
import respx
from httpx import Response

from soniox.client import AsyncSonioxClient, SonioxClient
from soniox.errors import (
    SonioxAPIError,
    SonioxAuthenticationError,
    SonioxConflictError,
    SonioxInvalidRequestError,
    SonioxNotFoundError,
    SonioxRateLimitError,
    SonioxServerError,
)
from soniox.types import ApiError
from tests.helpers import API_KEY, api_error_body, build

from ._openapi import OPERATIONS, Operation
from ._sdk_bindings import SDK_BINDINGS, SDK_BINDINGS_FULL, SdkBinding

# Cartesian of (operation, variant) - every op is tested at minimum args, and
# (where applicable) a second time with all optional fields populated. Catches
# "SDK silently drops a newly-added optional field" regressions.
#
# Operations without a binding are skipped here (test collection stays clean);
# ``test_all_operations_covered`` is the single place that reports them.
_LABELED_VARIANTS: list[tuple[Operation, str, SdkBinding]] = []
for _op in OPERATIONS:
    if _op.operation_id in SDK_BINDINGS:
        _LABELED_VARIANTS.append((_op, "min", SDK_BINDINGS[_op.operation_id]))
    if _op.operation_id in SDK_BINDINGS_FULL:
        _LABELED_VARIANTS.append((_op, "full", SDK_BINDINGS_FULL[_op.operation_id]))

_VARIANTS = [(op, binding) for op, _, binding in _LABELED_VARIANTS]
_VARIANT_IDS = [f"{op.operation_id}-{label}" for op, label, _ in _LABELED_VARIANTS]


def _mock_success(op: Operation) -> tuple[respx.Route, Any]:
    """Install a respx route returning the documented success shape for ``op``.

    Returns ``(route, expected_body)``. ``expected_body`` is ``None`` for 204
    responses so tests can assert ``result is None``.
    """
    if op.response_model is None:
        route = respx.request(op.http_method, op.url).mock(
            return_value=Response(op.success_status)
        )
        return route, None
    mock = build(op.response_model)
    route = respx.request(op.http_method, op.url).mock(
        return_value=Response(op.success_status, json=mock.model_dump(mode="json"))
    )
    return route, mock


def _assert_wire_contract(request: httpx.Request, op: Operation, binding: SdkBinding) -> None:
    """Assert the SDK issued exactly the request we expected for ``op``."""
    assert request.method == op.http_method
    assert str(request.url).split("?", 1)[0] == op.url
    assert request.headers["Authorization"] == f"Bearer {API_KEY}"

    for key, value in binding.expect_params.items():
        assert request.url.params[key] == value

    if binding.expect_json:
        sent = json.loads(request.content)
        for key, value in binding.expect_json.items():
            assert sent[key] == value

    if binding.expect_multipart:
        assert "multipart/form-data" in request.headers["Content-Type"]


# ---------------------------------------------------------------------------
# Coverage guard
# ---------------------------------------------------------------------------


def test_all_operations_covered() -> None:
    """Every OpenAPI operation must have an SDK binding."""
    missing = [op.operation_id for op in OPERATIONS if op.operation_id not in SDK_BINDINGS]
    assert not missing, (
        "New OpenAPI operations are missing SDK bindings. "
        "Add them to tests/unit/_sdk_bindings.py:\n  "
        + "\n  ".join(missing)
    )


# ---------------------------------------------------------------------------
# Happy path - per operation × (min, full) × (sync, async)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("op, binding", _VARIANTS, ids=_VARIANT_IDS)
@respx.mock
def test_happy_path_sync(
    client: SonioxClient, op: Operation, binding: SdkBinding
) -> None:
    route, expected = _mock_success(op)

    result = binding.sync_call(client)

    assert route.called
    _assert_wire_contract(route.calls.last.request, op, binding)
    if expected is not None:
        assert result == expected
    else:
        assert result is None


@pytest.mark.parametrize("op, binding", _VARIANTS, ids=_VARIANT_IDS)
@respx.mock
async def test_happy_path_async(
    async_client: AsyncSonioxClient, op: Operation, binding: SdkBinding
) -> None:
    route, expected = _mock_success(op)

    result = await binding.async_call(async_client)

    assert route.called
    _assert_wire_contract(route.calls.last.request, op, binding)
    if expected is not None:
        assert result == expected
    else:
        assert result is None


# ---------------------------------------------------------------------------
# Error mapping
# ---------------------------------------------------------------------------

STATUS_TO_EXC: list[tuple[int, type[SonioxAPIError]]] = [
    (400, SonioxInvalidRequestError),
    (401, SonioxAuthenticationError),
    (403, SonioxAuthenticationError),
    (404, SonioxNotFoundError),
    (409, SonioxConflictError),
    (429, SonioxRateLimitError),
    (500, SonioxServerError),
    (503, SonioxServerError),
]


@pytest.mark.parametrize("status, expected_exc", STATUS_TO_EXC)
@respx.mock
def test_error_mapping_with_api_error_body(
    client: SonioxClient, status: int, expected_exc: type[SonioxAPIError]
) -> None:
    """Status + structured body → typed exception + populated fields."""
    op = next(o for o in OPERATIONS if o.operation_id == "get_files")
    respx.get(op.url).mock(
        return_value=Response(status, json=api_error_body(status, message="specific message"))
    )

    with pytest.raises(expected_exc) as exc_info:
        SDK_BINDINGS[op.operation_id].sync_call(client)

    err = exc_info.value
    assert err.status_code == status
    assert err.request_id == "req_1"
    assert isinstance(err.api_error, ApiError)
    assert err.api_error.message == "specific message"
    assert "specific message" in str(err)


@pytest.mark.parametrize("status, expected_exc", STATUS_TO_EXC)
@respx.mock
def test_error_mapping_without_body(
    client: SonioxClient, status: int, expected_exc: type[SonioxAPIError]
) -> None:
    """Status with no JSON body → typed exception, no ``api_error``."""
    op = next(o for o in OPERATIONS if o.operation_id == "get_files")
    respx.get(op.url).mock(return_value=Response(status))

    with pytest.raises(expected_exc) as exc_info:
        SDK_BINDINGS[op.operation_id].sync_call(client)

    assert exc_info.value.status_code == status
    assert exc_info.value.api_error is None


@respx.mock
def test_error_validation_errors_appear_in_message(client: SonioxClient) -> None:
    body = api_error_body(
        400,
        message="Invalid payload",
        validation_errors=[
            {"error_type": "missing", "location": "body.audio_url", "message": "field required"}
        ],
    )
    respx.post("https://api.soniox.com/v1/transcriptions").mock(
        return_value=Response(400, json=body)
    )

    with pytest.raises(SonioxInvalidRequestError) as exc_info:
        client.stt.create(model="stt-async-v5", audio_url="https://example.com/audio.mp3")

    message = str(exc_info.value)
    assert "Invalid payload" in message
    assert "body.audio_url" in message
    assert "field required" in message


@respx.mock
def test_error_html_body_is_not_leaked(client: SonioxClient) -> None:
    """HTML gateway error pages fall back to the reason phrase (no raw HTML)."""
    respx.get("https://api.soniox.com/v1/files").mock(
        return_value=Response(502, text="<!DOCTYPE html><html>nope</html>")
    )
    with pytest.raises(SonioxServerError) as exc_info:
        client.files.list(limit=5)
    assert "<html" not in str(exc_info.value)


# ---------------------------------------------------------------------------
# Transport errors
# ---------------------------------------------------------------------------


@respx.mock
def test_timeout_propagates_sync(client: SonioxClient) -> None:
    respx.get("https://api.soniox.com/v1/files").mock(
        side_effect=httpx.TimeoutException("slow")
    )
    with pytest.raises(httpx.TimeoutException):
        client.files.list(limit=5)


@respx.mock
async def test_timeout_propagates_async(async_client: AsyncSonioxClient) -> None:
    respx.get("https://api.soniox.com/v1/files").mock(
        side_effect=httpx.TimeoutException("slow")
    )
    with pytest.raises(httpx.TimeoutException):
        await async_client.files.list(limit=5)
