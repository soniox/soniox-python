"""
Sync/async parity checks for the Soniox SDK.

When a new public method is added to a sync API class, the async twin must
get the same method. Without this test, someone could land a sync-only
``FilesAPI.count()`` and nothing in the suite would fail - until a user
hits ``AsyncFilesAPI.count()`` in production and gets ``AttributeError``.

Also enforces that every public method on an async class is actually a
coroutine or async generator - catches "copy-pasted from sync and forgot
``async``" mistakes.
"""

from __future__ import annotations

import inspect
from typing import Any

import pytest

from soniox.api.async_auth import AsyncAuthAPI
from soniox.api.async_files import AsyncFilesAPI
from soniox.api.async_models import AsyncModelsAPI
from soniox.api.async_stt import AsyncSttAPI
from soniox.api.async_webhooks import AsyncSonioxWebhooksAPI
from soniox.api.auth import AuthAPI
from soniox.api.files import FilesAPI
from soniox.api.models import ModelsAPI
from soniox.api.stt import SttAPI
from soniox.api.webhooks import SonioxWebhooksAPI
from soniox.client import AsyncSonioxClient, SonioxClient
from soniox.realtime.async_stt import AsyncRealtimeSTTClient, AsyncRealtimeSTTSession
from soniox.realtime.stt import RealtimeSTTClient, RealtimeSTTSession

from dataclasses import dataclass, field


@dataclass(frozen=True)
class ParityPair:
    """One (sync class, async class) pair with its known-good naming quirks."""

    label: str
    sync_cls: type
    async_cls: type
    # Sync name → async name renames specific to this pair.
    renames: dict[str, str] = field(default_factory=dict)
    # Method names that may appear only on the sync side.
    sync_only_ok: set[str] = field(default_factory=set)
    # Method names that may appear only on the async side.
    async_only_ok: set[str] = field(default_factory=set)
    # Method names that may be sync on the async class (pure CPU helpers).
    sync_methods_on_async_ok: set[str] = field(default_factory=set)


API_PAIRS: list[ParityPair] = [
    ParityPair(
        "SonioxClient",
        SonioxClient,
        AsyncSonioxClient,
        renames={"close": "aclose"},
    ),
    ParityPair("FilesAPI", FilesAPI, AsyncFilesAPI),
    ParityPair("SttAPI", SttAPI, AsyncSttAPI),
    ParityPair("ModelsAPI", ModelsAPI, AsyncModelsAPI),
    ParityPair("AuthAPI", AuthAPI, AsyncAuthAPI),
    ParityPair(
        "SonioxWebhooksAPI",
        SonioxWebhooksAPI,
        AsyncSonioxWebhooksAPI,
        # Webhook logic is pure (no IO) so none of the methods need to be
        # coroutines; the async class inherits the sync implementation.
        sync_methods_on_async_ok={"verify_signature", "unwrap", "webhook_payload"},
    ),
    ParityPair(
        "RealtimeSTTClient",
        RealtimeSTTClient,
        AsyncRealtimeSTTClient,
        # ``connect`` returns a session object; the session's __aenter__
        # does the actual network IO.
        sync_methods_on_async_ok={"connect"},
    ),
    ParityPair(
        "RealtimeSTTSession",
        RealtimeSTTSession,
        AsyncRealtimeSTTSession,
        async_only_ok={"aenter"},
        # ``parse_event`` is pure-CPU JSON parsing; intentionally sync on both.
        sync_methods_on_async_ok={"parse_event"},
    ),
]


def _public_callables(cls: type) -> set[str]:
    return {
        name
        for name in dir(cls)
        if not name.startswith("_") and callable(getattr(cls, name, None))
    }


@pytest.mark.parametrize("pair", API_PAIRS, ids=lambda p: p.label)
def test_api_public_methods_match(pair: ParityPair) -> None:
    sync_methods = _public_callables(pair.sync_cls)
    async_methods = _public_callables(pair.async_cls)

    reverse_renames = {v: k for k, v in pair.renames.items()}

    expected_async = {pair.renames.get(n, n) for n in sync_methods} | pair.async_only_ok
    expected_sync = {reverse_renames.get(n, n) for n in async_methods} | pair.sync_only_ok

    async_only = async_methods - expected_async
    sync_only = sync_methods - expected_sync

    diffs = []
    if sync_only:
        diffs.append(f"sync-only on {pair.label}: {sorted(sync_only)}")
    if async_only:
        diffs.append(f"async-only on {pair.label}: {sorted(async_only)}")
    assert not diffs, "\n".join(diffs)


@pytest.mark.parametrize("pair", API_PAIRS, ids=lambda p: p.label)
def test_async_methods_are_actually_async(pair: ParityPair) -> None:
    """Every public callable on an async class must be a coroutine or async
    generator, unless explicitly declared sync-on-async in the parity spec."""
    offenders: list[str] = []
    for name in _public_callables(pair.async_cls):
        if name in pair.sync_methods_on_async_ok:
            continue
        obj: Any = getattr(pair.async_cls, name)
        if inspect.iscoroutinefunction(obj) or inspect.isasyncgenfunction(obj):
            continue
        if isinstance(inspect.getattr_static(pair.async_cls, name, None), property):
            continue
        offenders.append(name)
    assert not offenders, (
        f"{pair.async_cls.__name__} has public method(s) that aren't async: {offenders}"
    )
