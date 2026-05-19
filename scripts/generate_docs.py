from __future__ import annotations

import ast
import re
import shutil
import textwrap
from dataclasses import dataclass, field
from pathlib import Path

from griffe import AliasResolutionError, Attribute, Class, Function, GriffeLoader, Module
from griffe._internal.models import Alias, Object

OUTPUT_DIR = Path("./docs")

ASYNC_DOC_PATH = OUTPUT_DIR / "async_client.md"
REALTIME_DOC_PATH = OUTPUT_DIR / "realtime_client.md"
TYPES_DOC_PATH = OUTPUT_DIR / "types.md"
UTILS_DOC_PATH = OUTPUT_DIR / "utils.md"

ASYNC_CLASS_SPECS = [
    ("soniox.client", "AsyncSonioxClient"),
    ("soniox.api.async_files", "AsyncFilesAPI"),
    ("soniox.api.async_stt", "AsyncSttAPI"),
    ("soniox.api.async_tts", "AsyncTtsAPI"),
    ("soniox.api.async_tts_models", "AsyncTtsModelsAPI"),
    ("soniox.api.async_models", "AsyncModelsAPI"),
    ("soniox.api.async_usage_logs", "AsyncUsageLogsAPI"),
    ("soniox.api.async_concurrency_limits", "AsyncConcurrencyLimitsAPI"),
    ("soniox.api.async_auth", "AsyncAuthAPI"),
    ("soniox.api.async_webhooks", "AsyncSonioxWebhooksAPI"),
]

ASYNC_PREAMBLE = (
    "> **Sync mirror:** the synchronous `SonioxClient` exposes the same API "
    "as `AsyncSonioxClient` below - drop `await` from each call and treat "
    "`AsyncIterator[X]` return types as plain `Iterator[X]`. Only the async "
    "surface is documented here to avoid duplicating an otherwise identical "
    "reference. Realtime sessions have genuinely different sync/async "
    "patterns and are documented in the [Realtime Client](./realtime_client.md) "
    "page."
)

REALTIME_CLASS_SPECS = [
    ("soniox.realtime", "RealtimeAPI"),
    ("soniox.realtime", "AsyncRealtimeAPI"),
    ("soniox.realtime.stt", "RealtimeSTTClient"),
    ("soniox.realtime.async_stt", "AsyncRealtimeSTTClient"),
    ("soniox.realtime.stt", "RealtimeSTTSession"),
    ("soniox.realtime.async_stt", "AsyncRealtimeSTTSession"),
    ("soniox.realtime.tts", "RealtimeTTSClient"),
    ("soniox.realtime.async_tts", "AsyncRealtimeTTSClient"),
    ("soniox.realtime.tts", "RealtimeTTSConnection"),
    ("soniox.realtime.async_tts", "AsyncRealtimeTTSConnection"),
    ("soniox.realtime.tts", "RealtimeTTSMultiplexedConnection"),
    ("soniox.realtime.async_tts", "AsyncRealtimeTTSMultiplexedConnection"),
    ("soniox.realtime.tts", "RealtimeTTSStream"),
    ("soniox.realtime.async_tts", "AsyncRealtimeTTSStream"),
]

TYPES_INIT_PATH = Path("./src/soniox/types/__init__.py")
UTILS_INIT_PATH = Path("./src/soniox/utils.py")


@dataclass
class ParsedDoc:
    summary: str = ""
    body: str = ""
    parameters: dict[str, str] = field(default_factory=dict)
    attributes: dict[str, str] = field(default_factory=dict)
    returns: str = ""
    yields: str = ""
    raises: list[tuple[str, str]] = field(default_factory=list)
    examples: list[str] = field(default_factory=list)


@dataclass
class SourceDocIndex:
    class_field_docs: dict[str, dict[str, str]] = field(default_factory=dict)
    symbol_docs: dict[str, str] = field(default_factory=dict)
    symbol_defs: dict[str, str] = field(default_factory=dict)


SECTION_HEADERS = {
    "args": "parameters",
    "arguments": "parameters",
    "parameters": "parameters",
    "attributes": "attributes",
    "returns": "returns",
    "yields": "yields",
    "raises": "raises",
    "example": "examples",
    "examples": "examples",
}

MODULE_CACHE: dict[str, Module] = {}
SOURCE_INDEX_CACHE: dict[Path, SourceDocIndex] = {}
PARAM_FALLBACK_CACHE: dict[tuple[Path, str], dict[str, str]] = {}
GLOBAL_TYPE_FIELD_DOCS_CACHE: dict[str, dict[str, str]] | None = None
GLOBAL_FIELD_NAME_DOCS_CACHE: dict[str, str] | None = None
GLOBAL_CLASS_SUMMARIES_CACHE: dict[str, str] | None = None
CLASS_PARAM_DOCS_CACHE: dict[str, dict[str, str]] = {}

DESCRIPTION_HINTS: dict[str, str] = {
    "api_key": "API key used for authentication.",
    "api_base_url": "Base URL for Soniox REST API requests.",
    "websocket_base_url": "Base URL for Soniox realtime WebSocket endpoint.",
    "tts_api_base_url": "Base URL for Soniox Text-to-Speech REST API requests.",
    "tts_websocket_base_url": "Base URL for Soniox Text-to-Speech realtime WebSocket endpoint.",
    "audio_url": "Publicly accessible audio URL.",
    "auth": "Authentication API namespace.",
    "client": "Soniox client instance.",
    "client_kwargs": "Additional HTTP client keyword arguments.",
    "client_reference_id": "Optional tracking identifier.",
    "config": "Configuration options for this operation.",
    "cursor": "Pagination cursor for the next page.",
    "data": "Form-encoded request payload.",
    "delete_after": "Whether to delete created resources after completion.",
    "expires_in_seconds": "Duration in seconds before expiration.",
    "file": "File input to upload or transcribe.",
    "file_id": "ID of a previously uploaded file.",
    "filename": "Filename associated with uploaded file data.",
    "files": "Multipart file payload mapping.",
    "finish": "Whether to send a finish signal after streaming completes.",
    "id": "Unique identifier.",
    "interval_sec": "Polling interval in seconds.",
    "json": "JSON request payload.",
    "limit": "Maximum number of items to return.",
    "method": "HTTP method to use for the request.",
    "model": "Speech-to-text model to use.",
    "params": "Query parameters for the request.",
    "path": "Relative API path for the request.",
    "raw": "Raw event payload from the realtime API.",
    "signal": "Optional cancellation signal.",
    "timeout_sec": "Maximum wait time in seconds.",
    "transcription_id": "Transcription identifier.",
    "usage_type": "Intended usage type for the temporary API key.",
    "url": "WebSocket URL for realtime transcription.",
    "webhook_auth": "Webhook authentication configuration.",
    "webhook_secret": "Webhook secret used for signature verification.",
    "webhook_signature_header": "Webhook signature header name.",
    "webhook_url": "URL to receive webhook notifications.",
    "audio_format": "Audio format for realtime transcription.",
    "num_channels": "Number of audio channels.",
    "sample_rate": "Audio sample rate in Hz.",
    "stt": "Speech-to-text API namespace.",
    "tts": "Text-to-Speech API namespace",
    "wait_interval_sec": "Polling interval in seconds while waiting.",
    "wait_timeout_sec": "Maximum wait time in seconds while polling.",
    "webhooks": "Webhook utilities API namespace.",
    "chunks": "Audio chunks to stream to realtime transcription.",
    "source_languages": "List of source language codes.",
    "exclude_source_languages": "Source language codes excluded for this target.",
    "target_language": "Target language code.",
}

SKIP_PROPERTY_NAMES = {"model_config", "enter", "aenter"}


def resolve_alias(member: Alias | Object | None):
    while isinstance(member, Alias):
        try:
            member = member.target
        except AliasResolutionError:
            return None
    return member


def load_module_cached(loader: GriffeLoader, module_name: str) -> Module:
    cached = MODULE_CACHE.get(module_name)
    if cached is not None:
        return cached
    loaded = loader.load(module_name)
    MODULE_CACHE[module_name] = loaded
    return loaded


def get_file_path(obj: Object | None) -> Path | None:
    if obj is None:
        return None
    raw = getattr(obj, "filepath", None)
    if raw is None:
        return None
    if isinstance(raw, Path):
        return raw
    if isinstance(raw, str):
        return Path(raw)
    if isinstance(raw, (tuple, list)) and raw:
        first = raw[0]
        if isinstance(first, Path):
            return first
        if isinstance(first, str):
            return Path(first)
    return None


def slugify(value: str) -> str:
    lowered = value.lower()
    lowered = re.sub(r"[^a-z0-9_]+", "-", lowered)
    return lowered.strip("-")


def escape_table_cell(value: str) -> str:
    if not value:
        return "-"
    return value.replace("|", "\\|").replace("\n", " ").strip() or "-"


def as_text(value: object | None) -> str:
    if value is None:
        return "-"
    text = str(value).strip()
    return text if text else "-"


def clean_paragraph_block(text: str) -> str:
    lines = [line.rstrip() for line in text.splitlines()]
    while lines and not lines[0].strip():
        lines.pop(0)
    while lines and not lines[-1].strip():
        lines.pop()
    out: list[str] = []
    blank = False
    for line in lines:
        if not line.strip():
            if not blank:
                out.append("")
            blank = True
        else:
            out.append(line.strip())
            blank = False
    return "\n".join(out).strip()


def extract_docstring_text(obj: Object) -> str:
    if not getattr(obj, "docstring", None):
        return ""
    return textwrap.dedent(obj.docstring.value).strip()


def parse_section_header(line: str) -> str | None:
    match = re.match(r"^\s*([A-Za-z][A-Za-z ]+):\s*$", line)
    if not match:
        return None
    normalized = match.group(1).strip().lower()
    return SECTION_HEADERS.get(normalized)


def parse_named_entries(lines: list[str]) -> dict[str, str]:
    entries: dict[str, str] = {}
    current_name: str | None = None
    current_desc: list[str] = []
    for raw in lines:
        line = raw.rstrip()
        if not line.strip():
            if current_desc:
                current_desc.append("")
            continue
        match = re.match(r"^\s*([A-Za-z_][\w\.\-]*)\s*(?:\(([^)]*)\))?\s*:\s*(.*)$", line)
        if match:
            if current_name is not None:
                entries[current_name] = clean_paragraph_block("\n".join(current_desc))
            current_name = match.group(1)
            current_desc = [match.group(3).strip()]
        elif current_name is not None:
            current_desc.append(line.strip())
    if current_name is not None:
        entries[current_name] = clean_paragraph_block("\n".join(current_desc))
    return {k: v for k, v in entries.items() if v}


def parse_raises_entries(lines: list[str]) -> list[tuple[str, str]]:
    entries: list[tuple[str, str]] = []
    current_name: str | None = None
    current_desc: list[str] = []
    for raw in lines:
        line = raw.rstrip()
        if not line.strip():
            if current_desc:
                current_desc.append("")
            continue
        match = re.match(r"^\s*([A-Za-z_][\w\.\[\], ]*)\s*:\s*(.*)$", line)
        if match:
            if current_name is not None:
                entries.append((current_name.strip(), clean_paragraph_block("\n".join(current_desc))))
            current_name = match.group(1)
            current_desc = [match.group(2).strip()]
        elif current_name is not None:
            current_desc.append(line.strip())
    if current_name is not None:
        entries.append((current_name.strip(), clean_paragraph_block("\n".join(current_desc))))
    return [(name, desc) for name, desc in entries if name or desc]


def parse_examples(lines: list[str]) -> list[str]:
    blocks: list[str] = []
    current: list[str] = []
    for raw in lines:
        if not raw.strip():
            if current:
                blocks.append(textwrap.dedent("\n".join(current)).strip("\n"))
                current = []
            continue
        current.append(raw)
    if current:
        blocks.append(textwrap.dedent("\n".join(current)).strip("\n"))
    return [block for block in blocks if block.strip()]


def parse_docstring(text: str) -> ParsedDoc:
    if not text:
        return ParsedDoc()
    lines = text.splitlines()
    narrative: list[str] = []
    sections: dict[str, list[str]] = {}
    current_section: str | None = None

    for line in lines:
        header = parse_section_header(line)
        if header:
            current_section = header
            sections.setdefault(current_section, [])
            continue
        if current_section is None:
            narrative.append(line)
        else:
            sections[current_section].append(line)

    body = clean_paragraph_block("\n".join(narrative))
    summary = body.splitlines()[0].strip() if body else ""

    result = ParsedDoc(summary=summary, body=body)
    result.parameters = parse_named_entries(sections.get("parameters", []))
    result.attributes = parse_named_entries(sections.get("attributes", []))
    result.returns = clean_paragraph_block("\n".join(sections.get("returns", [])))
    result.yields = clean_paragraph_block("\n".join(sections.get("yields", [])))
    result.raises = parse_raises_entries(sections.get("raises", []))
    result.examples = parse_examples(sections.get("examples", []))
    return result


def get_parsed_doc(obj: Object) -> ParsedDoc:
    return parse_docstring(extract_docstring_text(obj))


def extract_name_target(node: ast.AST) -> str | None:
    if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
        return node.targets[0].id
    if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
        return node.target.id
    return None


def extract_symbol_definition(source: str, node: ast.AST) -> str:
    if isinstance(node, ast.Assign):
        segment = ast.get_source_segment(source, node.value)
        if segment:
            return segment.strip()
        return ast.unparse(node.value).strip()
    if isinstance(node, ast.AnnAssign):
        value = node.value if node.value is not None else node.annotation
        if value is None:
            return ""
        segment = ast.get_source_segment(source, value)
        if segment:
            return segment.strip()
        return ast.unparse(value).strip()
    return ""


def extract_following_string(nodes: list[ast.stmt], index: int) -> str:
    if index >= len(nodes):
        return ""
    node = nodes[index]
    if isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant):
        if isinstance(node.value.value, str):
            return node.value.value
    return ""


def get_source_index(path: Path | None) -> SourceDocIndex:
    if path is None:
        return SourceDocIndex()

    normalized = path.resolve()
    cached = SOURCE_INDEX_CACHE.get(normalized)
    if cached is not None:
        return cached

    if not normalized.exists():
        empty = SourceDocIndex()
        SOURCE_INDEX_CACHE[normalized] = empty
        return empty

    source = normalized.read_text(encoding="utf-8")
    tree = ast.parse(source)
    index = SourceDocIndex()

    for i, stmt in enumerate(tree.body):
        if isinstance(stmt, ast.ClassDef):
            class_fields: dict[str, str] = {}
            for j, class_stmt in enumerate(stmt.body):
                field_name = extract_name_target(class_stmt)
                if not field_name or field_name.startswith("_"):
                    continue
                doc = extract_following_string(stmt.body, j + 1)
                if doc:
                    class_fields[field_name] = clean_paragraph_block(textwrap.dedent(doc))
            if class_fields:
                index.class_field_docs[stmt.name] = class_fields
            continue

        symbol_name = extract_name_target(stmt)
        if not symbol_name:
            continue

        symbol_definition = extract_symbol_definition(source, stmt)
        if symbol_definition:
            index.symbol_defs[symbol_name] = symbol_definition

        symbol_doc = extract_following_string(tree.body, i + 1)
        if symbol_doc:
            index.symbol_docs[symbol_name] = clean_paragraph_block(textwrap.dedent(symbol_doc))

    SOURCE_INDEX_CACHE[normalized] = index
    return index


def parse_dunder_all(path: Path) -> list[str]:
    if not path.exists():
        return []
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source)
    for stmt in tree.body:
        name = extract_name_target(stmt)
        if name != "__all__":
            continue
        value = stmt.value if isinstance(stmt, ast.Assign) else stmt.value if isinstance(stmt, ast.AnnAssign) else None
        if not isinstance(value, (ast.List, ast.Tuple)):
            continue
        exports: list[str] = []
        for elt in value.elts:
            if isinstance(elt, ast.Constant) and isinstance(elt.value, str):
                exports.append(elt.value)
        return exports
    return []


def get_global_type_field_docs() -> dict[str, dict[str, str]]:
    global GLOBAL_TYPE_FIELD_DOCS_CACHE
    if GLOBAL_TYPE_FIELD_DOCS_CACHE is not None:
        return GLOBAL_TYPE_FIELD_DOCS_CACHE

    merged: dict[str, dict[str, str]] = {}
    types_dir = Path("./src/soniox/types")
    for py_file in sorted(types_dir.glob("*.py")):
        if py_file.name == "__init__.py":
            continue
        source_index = get_source_index(py_file)
        for class_name, field_docs in source_index.class_field_docs.items():
            merged[class_name] = dict(field_docs)

    GLOBAL_TYPE_FIELD_DOCS_CACHE = merged
    return merged


def _pick_best_description(descriptions: list[str]) -> str:
    cleaned = [clean_paragraph_block(d) for d in descriptions if d and clean_paragraph_block(d)]
    if not cleaned:
        return ""
    frequency: dict[str, int] = {}
    for desc in cleaned:
        frequency[desc] = frequency.get(desc, 0) + 1
    return sorted(cleaned, key=lambda d: (frequency[d], len(d), d), reverse=True)[0]


def get_global_field_name_docs() -> dict[str, str]:
    global GLOBAL_FIELD_NAME_DOCS_CACHE
    if GLOBAL_FIELD_NAME_DOCS_CACHE is not None:
        return GLOBAL_FIELD_NAME_DOCS_CACHE

    buckets: dict[str, list[str]] = {}
    for field_docs in get_global_type_field_docs().values():
        for field_name, description in field_docs.items():
            if not description:
                continue
            buckets.setdefault(field_name, []).append(description)

    GLOBAL_FIELD_NAME_DOCS_CACHE = {
        field_name: _pick_best_description(descriptions)
        for field_name, descriptions in buckets.items()
    }
    return GLOBAL_FIELD_NAME_DOCS_CACHE


def get_global_class_summaries() -> dict[str, str]:
    global GLOBAL_CLASS_SUMMARIES_CACHE
    if GLOBAL_CLASS_SUMMARIES_CACHE is not None:
        return GLOBAL_CLASS_SUMMARIES_CACHE

    summaries: dict[str, str] = {}
    source_root = Path("./src/soniox")
    for py_file in source_root.rglob("*.py"):
        source = py_file.read_text(encoding="utf-8")
        tree = ast.parse(source)
        for stmt in tree.body:
            if not isinstance(stmt, ast.ClassDef):
                continue
            class_doc = ast.get_docstring(stmt) or ""
            summary = clean_paragraph_block(class_doc).splitlines()[0].strip() if class_doc else ""
            if summary and stmt.name not in summaries:
                summaries[stmt.name] = summary

    GLOBAL_CLASS_SUMMARIES_CACHE = summaries
    return summaries


def extract_type_names(type_text: str) -> list[str]:
    if not type_text or type_text == "-":
        return []
    return re.findall(r"\b[A-Z][A-Za-z0-9_]*\b", type_text)


def annotation_summary(type_text: str) -> str:
    summaries = get_global_class_summaries()
    for type_name in extract_type_names(type_text):
        summary = summaries.get(type_name)
        if summary:
            return summary
    return ""


def class_param_docs(cls: Class) -> dict[str, str]:
    cache_key = cls.path
    cached = CLASS_PARAM_DOCS_CACHE.get(cache_key)
    if cached is not None:
        return cached

    docs_map: dict[str, str] = {}
    for member in cls.members.values():
        resolved = resolve_alias(member)
        if not isinstance(resolved, Function):
            continue
        doc = get_parsed_doc(resolved)
        for name, description in doc.parameters.items():
            if description and name not in docs_map:
                docs_map[name] = description
        fallback = get_function_param_fallback_map(resolved)
        for name, description in fallback.items():
            if description and name not in docs_map:
                docs_map[name] = description

    CLASS_PARAM_DOCS_CACHE[cache_key] = docs_map
    return docs_map


def best_effort_description(name: str, type_text: str = "") -> str:
    if name in DESCRIPTION_HINTS:
        return DESCRIPTION_HINTS[name]

    global_by_name = get_global_field_name_docs()
    if name in global_by_name:
        return global_by_name[name]

    summary = annotation_summary(type_text)
    if summary:
        return summary

    if name.endswith("_id"):
        prefix = name[:-3].replace("_", " ").strip()
        if prefix:
            return f"{prefix.capitalize()} identifier."
        return "Resource identifier."

    if name.startswith("enable_"):
        feature = name[len("enable_") :].replace("_", " ")
        return f"Whether to enable {feature}."

    return ""


def get_function_key(fn: Function) -> str:
    parent = getattr(fn, "parent", None)
    if isinstance(parent, Class):
        return f"{parent.name}.{fn.name}"
    return fn.name


def get_call_name(call: ast.Call) -> str | None:
    if isinstance(call.func, ast.Name):
        return call.func.id
    if isinstance(call.func, ast.Attribute):
        return call.func.attr
    return None


def iter_function_nodes(tree: ast.Module) -> list[tuple[str, ast.FunctionDef | ast.AsyncFunctionDef]]:
    nodes: list[tuple[str, ast.FunctionDef | ast.AsyncFunctionDef]] = []
    for stmt in tree.body:
        if isinstance(stmt, (ast.FunctionDef, ast.AsyncFunctionDef)):
            nodes.append((stmt.name, stmt))
        elif isinstance(stmt, ast.ClassDef):
            for class_stmt in stmt.body:
                if isinstance(class_stmt, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    nodes.append((f"{stmt.name}.{class_stmt.name}", class_stmt))
    return nodes


def get_function_param_fallback_map(fn: Function) -> dict[str, str]:
    file_path = get_file_path(fn)
    if file_path is None:
        return {}
    normalized = file_path.resolve()
    function_key = get_function_key(fn)
    cache_key = (normalized, function_key)
    cached = PARAM_FALLBACK_CACHE.get(cache_key)
    if cached is not None:
        return cached

    if not normalized.exists():
        PARAM_FALLBACK_CACHE[cache_key] = {}
        return {}

    source = normalized.read_text(encoding="utf-8")
    tree = ast.parse(source)
    function_nodes = dict(iter_function_nodes(tree))
    node = function_nodes.get(function_key)
    if node is None:
        PARAM_FALLBACK_CACHE[cache_key] = {}
        return {}

    arg_names: set[str] = set()
    arg_names.update(arg.arg for arg in node.args.posonlyargs)
    arg_names.update(arg.arg for arg in node.args.args)
    arg_names.update(arg.arg for arg in node.args.kwonlyargs)
    arg_names.discard("self")
    arg_names.discard("cls")

    type_field_docs = get_global_type_field_docs()
    fallback: dict[str, str] = {}

    for ast_node in ast.walk(node):
        if not isinstance(ast_node, ast.Call):
            continue
        call_name = get_call_name(ast_node)
        if not call_name:
            continue
        call_field_docs = type_field_docs.get(call_name)
        if not call_field_docs:
            continue

        for kw in ast_node.keywords:
            if kw.arg is None:
                continue
            if not isinstance(kw.value, ast.Name):
                continue
            param_name = kw.value.id
            if param_name not in arg_names:
                continue
            if param_name in fallback:
                continue
            desc = call_field_docs.get(kw.arg, "")
            if desc:
                fallback[param_name] = desc

    PARAM_FALLBACK_CACHE[cache_key] = fallback
    return fallback


def is_public_function(fn: Function) -> bool:
    return fn.name == "__init__" or not fn.name.startswith("_")


def is_public_attribute(attr: Attribute) -> bool:
    return not attr.name.startswith("_")


def is_property_method(fn: Function) -> bool:
    decorators = getattr(fn, "decorators", []) or []
    for decorator in decorators:
        text = str(getattr(decorator, "value", decorator))
        if text.endswith("property") or "cached_property" in text:
            return True
    return False


def method_heading(name: str) -> str:
    return f"{name}()"


def format_signature(fn: Function) -> str:
    return str(fn.signature())


def format_constructor_signature(cls: Class, constructor: Function) -> str:
    sig_text = str(constructor.signature())
    match = re.match(r"^__init__\((.*)\)\s*->\s*None$", sig_text)
    if not match:
        return f"{cls.name}{sig_text[sig_text.find('('):]}"
    params = match.group(1).strip()
    if params.startswith("self, "):
        params = params[len("self, ") :]
    elif params == "self":
        params = ""
    return f"{cls.name}({params})"


def render_parameters_table(fn: Function, docs: ParsedDoc) -> str:
    fallback_docs = get_function_param_fallback_map(fn)
    shared_docs: dict[str, str] = {}
    if isinstance(getattr(fn, "parent", None), Class):
        shared_docs = class_param_docs(fn.parent)
    rows: list[str] = []
    for param in fn.parameters:
        if param.name in {"self", "cls", "/", "*"}:
            continue
        param_name = f"`{param.name}`"
        annotation_text = as_text(param.annotation)
        param_type = f"`{escape_table_cell(annotation_text)}`"
        desc_value = docs.parameters.get(param.name, "")
        if not desc_value:
            desc_value = fallback_docs.get(param.name, "")
        if not desc_value:
            desc_value = shared_docs.get(param.name, "")
        if not desc_value:
            desc_value = best_effort_description(param.name, annotation_text)
        desc = escape_table_cell(desc_value)
        rows.append(f"| {param_name} | {param_type} | {desc} |")
    if not rows:
        return ""
    out = [
        "**Parameters**",
        "",
        "| Parameter | Type | Description |",
        "| ------ | ------ | ------ |",
        *rows,
    ]
    return "\n".join(out)


def render_returns(fn: Function, docs: ParsedDoc) -> str:
    if docs.yields:
        lines = ["**Yields**", "", f"`{as_text(fn.returns)}`", "", docs.yields]
        return "\n".join(lines)
    if fn.returns is None and not docs.returns:
        return ""
    lines = ["**Returns**", "", f"`{as_text(fn.returns)}`"]
    if docs.returns:
        lines.extend(["", docs.returns])
    return "\n".join(lines)


def render_raises(docs: ParsedDoc) -> str:
    if not docs.raises:
        return ""
    lines = ["**Raises**", ""]
    for exc, desc in docs.raises:
        if exc and desc:
            lines.append(f"- `{exc}` {desc}")
        elif exc:
            lines.append(f"- `{exc}`")
        elif desc:
            lines.append(f"- {desc}")
    return "\n".join(lines)


def render_examples(docs: ParsedDoc) -> str:
    if not docs.examples:
        return ""
    heading = "**Example**" if len(docs.examples) == 1 else "**Examples**"
    parts = [heading]
    for block in docs.examples:
        if "```" in block:
            parts.extend(["", block])
        else:
            parts.extend(["", "```python", block, "```"])
    return "\n".join(parts)


def get_class_field_docs(cls: Class) -> dict[str, str]:
    source_index = get_source_index(get_file_path(cls))
    return source_index.class_field_docs.get(cls.name, {})


def render_method(fn: Function, class_slug: str) -> str:
    docs = get_parsed_doc(fn)
    anchor_id = f"{class_slug}-{slugify(fn.name)}"
    sections = [
        f'<a id="{anchor_id}"></a>',
        "",
        f"### {method_heading(fn.name)}",
        "",
        "```python",
        format_signature(fn),
        "```",
    ]
    if docs.body:
        sections.extend(["", docs.body])

    parameters = render_parameters_table(fn, docs)
    if parameters:
        sections.extend(["", parameters])
    returns = render_returns(fn, docs)
    if returns:
        sections.extend(["", returns])
    raises = render_raises(docs)
    if raises:
        sections.extend(["", raises])
    examples = render_examples(docs)
    if examples:
        sections.extend(["", examples])
    return "\n".join(sections).strip()


def render_constructor(cls: Class, constructor: Function, class_slug: str) -> str:
    docs = get_parsed_doc(constructor)
    sections = [
        f'<a id="{class_slug}-constructor"></a>',
        "",
        "### Constructor",
        "",
        "```python",
        format_constructor_signature(cls, constructor),
        "```",
    ]
    if docs.body:
        sections.extend(["", docs.body])

    parameters = render_parameters_table(constructor, docs)
    if parameters:
        sections.extend(["", parameters])
    returns = render_returns(constructor, docs)
    if returns:
        sections.extend(["", returns])
    raises = render_raises(docs)
    if raises:
        sections.extend(["", raises])
    examples = render_examples(docs)
    if examples:
        sections.extend(["", examples])
    return "\n".join(sections).strip()


def render_properties(cls: Class, class_slug: str) -> str:
    class_docs = get_parsed_doc(cls)
    source_field_docs = get_class_field_docs(cls)
    global_field_docs = get_global_field_name_docs()
    rows: list[str] = []

    for member in cls.members.values():
        resolved = resolve_alias(member)
        if not isinstance(resolved, Attribute):
            continue
        if not is_public_attribute(resolved):
            continue
        if resolved.name in SKIP_PROPERTY_NAMES:
            continue
        desc = ""
        if getattr(resolved, "docstring", None):
            desc = parse_docstring(extract_docstring_text(resolved)).body
        if not desc:
            desc = class_docs.attributes.get(resolved.name, "")
        if not desc:
            desc = source_field_docs.get(resolved.name, "")
        if not desc:
            desc = global_field_docs.get(resolved.name, "")
        annotation_text = as_text(getattr(resolved, "annotation", None))
        if not desc:
            desc = best_effort_description(resolved.name, annotation_text)

        prop_name = f"`{resolved.name}`"
        prop_type = f"`{escape_table_cell(annotation_text)}`"
        rows.append(f"| {prop_name} | {prop_type} | {escape_table_cell(desc)} |")

    for member in cls.members.values():
        resolved = resolve_alias(member)
        if not isinstance(resolved, Function):
            continue
        if not is_public_function(resolved):
            continue
        if not is_property_method(resolved):
            continue
        if resolved.name in SKIP_PROPERTY_NAMES:
            continue
        prop_docs = get_parsed_doc(resolved)
        desc = prop_docs.body or prop_docs.summary
        return_type = as_text(resolved.returns)
        if not desc:
            desc = best_effort_description(resolved.name, return_type)
        prop_name = f"`{resolved.name}`"
        prop_type = f"`{escape_table_cell(return_type)}`"
        rows.append(f"| {prop_name} | {prop_type} | {escape_table_cell(desc)} |")

    if not rows:
        return ""

    lines = [
        f'<a id="{class_slug}-properties"></a>',
        "",
        "### Properties",
        "",
        "| Property | Type | Description |",
        "| ------ | ------ | ------ |",
        *rows,
    ]
    return "\n".join(lines)


def render_class(cls: Class) -> str:
    class_slug = slugify(cls.name)
    class_docs = get_parsed_doc(cls)
    sections: list[str] = [f"## {cls.name}"]
    if class_docs.body:
        sections.extend(["", class_docs.body])

    constructor = None
    methods: list[Function] = []
    for member in cls.members.values():
        resolved = resolve_alias(member)
        if not isinstance(resolved, Function):
            continue
        if not is_public_function(resolved):
            continue
        if resolved.name == "__init__":
            constructor = resolved
            continue
        if is_property_method(resolved):
            continue
        methods.append(resolved)

    if constructor is not None:
        sections.extend(["", render_constructor(cls, constructor, class_slug)])

    properties = render_properties(cls, class_slug)
    if properties:
        sections.extend(["", properties])

    if methods:
        method_blocks = [render_method(method, class_slug) for method in methods]
        sections.extend(["", "\n\n***\n\n".join(method_blocks)])

    return "\n".join(sections).strip()


def render_module_function(fn: Function) -> str:
    docs = get_parsed_doc(fn)
    anchor = slugify(fn.name)
    sections = [
        f'<a id="{anchor}"></a>',
        "",
        f"## {method_heading(fn.name)}",
        "",
        "```python",
        format_signature(fn),
        "```",
    ]
    if docs.body:
        sections.extend(["", docs.body])

    parameters = render_parameters_table(fn, docs)
    if parameters:
        sections.extend(["", parameters])
    returns = render_returns(fn, docs)
    if returns:
        sections.extend(["", returns])
    raises = render_raises(docs)
    if raises:
        sections.extend(["", raises])
    examples = render_examples(docs)
    if examples:
        sections.extend(["", examples])
    return "\n".join(sections).strip()


def get_symbol_description(export_name: str, symbol: Object) -> str:
    docs = get_parsed_doc(symbol)
    if docs.body:
        return docs.body
    source_index = get_source_index(get_file_path(symbol))
    if symbol.name in source_index.symbol_docs:
        return source_index.symbol_docs[symbol.name]
    if export_name in source_index.symbol_docs:
        return source_index.symbol_docs[export_name]
    return ""


def get_symbol_definition(export_name: str, symbol: Object) -> str:
    source_index = get_source_index(get_file_path(symbol))

    definition = ""
    if symbol.name in source_index.symbol_defs:
        definition = source_index.symbol_defs[symbol.name]
    elif export_name in source_index.symbol_defs:
        definition = source_index.symbol_defs[export_name]
    else:
        value = getattr(symbol, "value", None)
        if value is not None:
            definition = str(value).strip()
        if not definition:
            annotation = getattr(symbol, "annotation", None)
            if annotation is not None:
                definition = str(annotation).strip()

    if not definition:
        return export_name

    left_side = definition.split("=", 1)[0].strip()
    if "=" in definition and left_side == export_name:
        return definition

    return f"{export_name} = {definition}"


def render_type_symbol(export_name: str, symbol: Object) -> str:
    description = get_symbol_description(export_name, symbol)
    definition = get_symbol_definition(export_name, symbol)
    anchor = slugify(export_name)
    sections = [
        f'<a id="{anchor}"></a>',
        "",
        f"## {export_name}",
        "",
        "```python",
        definition,
        "```",
    ]
    if description:
        sections.extend(["", description])
    return "\n".join(sections).strip()


def yaml_escape(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"')


def render_frontmatter(title: str, description: str, keywords: list[str]) -> str:
    return (
        "---\n"
        f'title: "{yaml_escape(title)}"\n'
        f'description: "{yaml_escape(description)}"\n'
        f'keywords: "{yaml_escape(", ".join(keywords))}"\n'
        "---"
    )


def write_document(
    path: Path,
    *,
    title: str,
    description: str,
    keywords: list[str],
    sections: list[str],
) -> None:
    chunks = [render_frontmatter(title, description, keywords), *[s for s in sections if s.strip()]]
    content = "\n\n---\n\n".join(chunks)
    path.write_text(content, encoding="utf-8")
    print(f"Written {path}")


def resolve_class_specs(loader: GriffeLoader, specs: list[tuple[str, str]]) -> list[Class]:
    selected: list[Class] = []
    for module_name, class_name in specs:
        module = load_module_cached(loader, module_name)
        member = resolve_alias(module.members.get(class_name))
        if not isinstance(member, Class):
            print(f"Warning: {class_name} not found in {module_name}")
            continue
        selected.append(member)
    return selected


def collect_module_exports(
    loader: GriffeLoader, module_name: str, export_names: list[str]
) -> list[tuple[str, Object]]:
    module = load_module_cached(loader, module_name)
    collected: list[tuple[str, Object]] = []
    for export_name in export_names:
        member = resolve_alias(module.members.get(export_name))
        if member is None:
            print(f"Warning: export {export_name} not found in {module_name}")
            continue
        collected.append((export_name, member))
    return collected


def cleanup_legacy_docs() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    legacy_tree = OUTPUT_DIR / "soniox"
    if legacy_tree.exists():
        shutil.rmtree(legacy_tree)

    keep_names = {
        ASYNC_DOC_PATH.name,
        REALTIME_DOC_PATH.name,
        TYPES_DOC_PATH.name,
        UTILS_DOC_PATH.name,
    }
    for markdown_file in OUTPUT_DIR.glob("*.md"):
        if markdown_file.name not in keep_names:
            markdown_file.unlink()


def build_async_client_doc(loader: GriffeLoader) -> None:
    classes = resolve_class_specs(loader, ASYNC_CLASS_SPECS)
    sections = [ASYNC_PREAMBLE, *(render_class(cls) for cls in classes)]
    write_document(
        ASYNC_DOC_PATH,
        title="Async Client",
        description="Soniox Python SDK - Async Client Reference",
        keywords=[cls.name for cls in classes],
        sections=sections,
    )


def build_realtime_client_doc(loader: GriffeLoader) -> None:
    classes = resolve_class_specs(loader, REALTIME_CLASS_SPECS)
    sections = [render_class(cls) for cls in classes]
    write_document(
        REALTIME_DOC_PATH,
        title="Realtime Client",
        description="Soniox Python SDK - Realtime Client Reference",
        keywords=[cls.name for cls in classes],
        sections=sections,
    )


def build_types_doc(loader: GriffeLoader) -> None:
    export_names = parse_dunder_all(TYPES_INIT_PATH)
    exports = collect_module_exports(loader, "soniox.types", export_names)
    sections: list[str] = []
    for export_name, symbol in exports:
        if isinstance(symbol, Class):
            sections.append(render_class(symbol))
        elif isinstance(symbol, Function):
            sections.append(render_module_function(symbol))
        else:
            sections.append(render_type_symbol(export_name, symbol))

    write_document(
        TYPES_DOC_PATH,
        title="Types",
        description="Soniox Python SDK - Types Reference",
        keywords=export_names,
        sections=sections,
    )


def build_utils_doc(loader: GriffeLoader) -> None:
    export_names = parse_dunder_all(UTILS_INIT_PATH)
    exports = collect_module_exports(loader, "soniox.utils", export_names)
    sections = [render_module_function(sym) for _, sym in exports if isinstance(sym, Function)]
    write_document(
        UTILS_DOC_PATH,
        title="Helpers",
        description="Soniox Python SDK - Helper Functions Reference",
        keywords=export_names,
        sections=sections,
    )


def main() -> None:
    cleanup_legacy_docs()
    loader = GriffeLoader(search_paths=["./src", "../src"])
    build_async_client_doc(loader)
    build_realtime_client_doc(loader)
    build_types_doc(loader)
    build_utils_doc(loader)


if __name__ == "__main__":
    main()
