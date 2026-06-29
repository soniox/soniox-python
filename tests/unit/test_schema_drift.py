"""
Schema drift tests: catch SDK models falling out of sync with the upstream
OpenAPI schema.

We validate that, for every schema in ``components.schemas`` that maps to a
Pydantic model on ``soniox.types``:

- every field in the OpenAPI schema exists on the SDK model
- every field marked ``required`` in the OpenAPI schema is required on the SDK
  model (no default / not Optional)

The reverse direction (SDK fields not in OpenAPI) is intentionally not checked:
the SDK carries a few convenience fields that the server never returns.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from pydantic import BaseModel

from soniox import types

SCHEMA_PATH = Path("tests/data/openapi.json")

# Fields the SDK deliberately keeps optional even though the OpenAPI schema
# marks them required. Usually because older server versions omit the field,
# or because the SDK wants a sensible default. Re-evaluate periodically.
KNOWN_REQUIRED_DRIFT: set[str] = {
    "ApiError.request_id",
    "ApiError.validation_errors",
    "CreateTranscriptionPayload.model",
    "Model.aliased_model_id",
    "Model.supports_max_endpoint_delay",
    "Model.supports_endpoint_sensitivity",
    "Model.supports_endpoint_latency_adjustment",
    "Model.endpoint_latency_adjustment_max_level",
    "TTSModel.aliased_model_id",
    "TTSModel.languages",
}


def _load_component_schemas() -> dict[str, dict]:
    if not SCHEMA_PATH.exists():
        pytest.skip("openapi.json not found")
    return json.loads(SCHEMA_PATH.read_text())["components"]["schemas"]


def _sdk_model(name: str) -> type[BaseModel] | None:
    cls = getattr(types, name, None)
    if isinstance(cls, type) and issubclass(cls, BaseModel):
        return cls
    return None


def _sdk_models() -> list[tuple[str, type[BaseModel], dict]]:
    out = []
    for name, schema in _load_component_schemas().items():
        model = _sdk_model(name)
        if model is not None:
            out.append((name, model, schema))
    return out


def test_all_schema_fields_exist_in_sdk() -> None:
    missing: list[str] = []
    for name, model, schema in _sdk_models():
        sdk_fields = set(model.model_fields)
        for prop in schema.get("properties", {}):
            if prop not in sdk_fields:
                missing.append(f"{name}.{prop}")
    assert not missing, "SDK models missing OpenAPI fields:\n  " + "\n  ".join(sorted(missing))


def test_required_fields_are_required_in_sdk() -> None:
    """A field required by the server must not be Optional / have a default in the SDK."""
    drift: list[str] = []
    for name, model, schema in _sdk_models():
        required_in_schema = set(schema.get("required", []))
        for prop in required_in_schema:
            sdk_field = model.model_fields.get(prop)
            if sdk_field is None:
                continue  # already reported by the other test
            qualified = f"{name}.{prop}"
            if not sdk_field.is_required() and qualified not in KNOWN_REQUIRED_DRIFT:
                drift.append(qualified)
    assert not drift, (
        "Required-field drift (add to KNOWN_REQUIRED_DRIFT only if intentional):\n  "
        + "\n  ".join(sorted(drift))
    )


def test_at_least_one_model_was_checked() -> None:
    """Guard against the schema/type-module wiring silently breaking."""
    assert _sdk_models(), "No SDK models matched the OpenAPI schema - check imports"
