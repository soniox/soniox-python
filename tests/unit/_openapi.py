"""
OpenAPI schema introspection for tests.

Reads ``tests/data/openapi.json`` at import time and exposes a structured list
of operations. Used to drive parametrized tests so that adding a new endpoint
to the schema surfaces as a test failure (missing SDK binding) rather than
silently going uncovered.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path

from soniox import types as sdk_types

# Placeholder value substituted into every ``{path_param}`` so endpoint URLs
# are fully qualified for use with respx matchers.
PATH_PARAM_VALUE = "abc-123"

_SCHEMA_PATH = Path(__file__).parents[1] / "data" / "openapi.json"


@dataclass(frozen=True)
class Operation:
    """A single OpenAPI operation paired with everything a test needs to mock it."""

    operation_id: str
    http_method: str           # "GET" / "POST" / "DELETE"
    url: str                   # fully qualified, with path params substituted
    success_status: int        # 200, 201, or 204
    response_model: type | None  # SDK Pydantic class, or None for 204


def _resolve_success_status(responses: dict) -> int:
    for status in ("204", "201", "200"):
        if status in responses:
            return int(status)
    raise ValueError(f"No 2xx response in {responses.keys()}")


def _resolve_response_model(responses: dict, status: int) -> type | None:
    schema = (
        responses.get(str(status), {})
        .get("content", {})
        .get("application/json", {})
        .get("schema", {})
    )
    ref = schema.get("$ref")
    if not ref:
        return None
    model_name = ref.rsplit("/", 1)[-1]
    return getattr(sdk_types, model_name, None)


def _substitute_path_params(path: str) -> str:
    return re.sub(r"\{[^}]+\}", PATH_PARAM_VALUE, path)


def load_operations() -> list[Operation]:
    """Parse ``openapi.json`` into a flat list of :class:`Operation`s."""
    schema = json.loads(_SCHEMA_PATH.read_text())
    base_url = "https://api.soniox.com"  # schema paths are already /v1/...

    out: list[Operation] = []
    for path, methods in schema["paths"].items():
        for http_method, op in methods.items():
            op_id = op.get("operationId")
            if not op_id:
                continue
            status = _resolve_success_status(op.get("responses", {}))
            model = _resolve_response_model(op.get("responses", {}), status)
            out.append(
                Operation(
                    operation_id=op_id,
                    http_method=http_method.upper(),
                    url=base_url + _substitute_path_params(path),
                    success_status=status,
                    response_model=model,
                )
            )
    return out


OPERATIONS: list[Operation] = load_operations()
