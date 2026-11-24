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

import ast
import difflib
import inspect
import re
from dataclasses import dataclass, field
from pathlib import Path
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
        name for name in dir(cls) if not name.startswith("_") and callable(getattr(cls, name, None))
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


# The two realtime STT sessions are hand-written mirrors of each other, and the
# reconnect protocol is the most intricate thing in either. A fix that lands in
# one and not the other is a wrong transcript on the half that missed it, so
# these methods are compared body for body.
MIRRORED_METHODS: tuple[str, ...] = (
    "_can_resume",
    "_continue_stream",
    "_dial_once",
    "_end_a_stream_with_no_socket",
    "_for_caller",
)

# Written one way in the sync session and another in the async one, for reasons
# that are not drift: a different library call for the same act, or a different
# way to wait. Everything else must match.
SPELLINGS: tuple[tuple[str, str], ...] = (
    ("async def", "def"),
    ("await ", ""),
    ("async with", "with"),
    ("asyncio.sleep", "time.sleep"),
    ("async_ws_connect", "sync_ws_connect"),
    ("ws.transport.abort()", "ws.close_socket()"),
    # The async half has no thread to race, so it takes no lock to read the
    # ping log; the sync half must.
    ("with self._lock:\n    overdue", "overdue"),
)

# A bounded read: the sync socket takes a timeout, the async one is wrapped.
BOUNDED_READ = re.compile(r"asyncio\.wait_for\(ws\.recv\(\), (.+)\)")


def _normalised_method(path: Path, name: str) -> str:
    """One method's body, in a form the two halves can be compared in.

    `ast.unparse` throws away comments, docstrings and line wrapping, which are
    all free to differ, and leaves the code itself in one canonical spelling.
    """
    tree = ast.parse(path.read_text())
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == name:
            body = node.body[1:] if ast.get_docstring(node) else node.body
            source = "\n".join(ast.unparse(statement) for statement in body)
            for mine, theirs in SPELLINGS:
                source = source.replace(mine, theirs)
            return BOUNDED_READ.sub(r"ws.recv(timeout=\1)", source)
    raise AssertionError(f"{name} is not in {path.name}")


@pytest.mark.parametrize("name", MIRRORED_METHODS)
def test_the_reconnect_halves_have_not_drifted(name: str) -> None:
    # The files in this checkout, not wherever the package is installed: an
    # older copy on the path would fail this for the wrong reason, or pass it
    # while the two halves in front of you have drifted apart.
    realtime = Path(__file__).resolve().parents[2] / "src" / "soniox" / "realtime"
    sync = _normalised_method(realtime / "stt.py", name)
    asynchronous = _normalised_method(realtime / "async_stt.py", name)

    if sync != asynchronous:
        drift = "\n".join(
            difflib.unified_diff(
                sync.splitlines(),
                asynchronous.splitlines(),
                fromfile=f"stt.py {name}",
                tofile=f"async_stt.py {name}",
                lineterm="",
            )
        )
        raise AssertionError(f"the two halves of {name} no longer agree:\n{drift}")
