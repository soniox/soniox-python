from __future__ import annotations

import re
import textwrap
from dataclasses import dataclass, field
from pathlib import Path

from griffe import AliasResolutionError, Attribute, Class, Function, GriffeLoader, Module
from griffe._internal.models import Alias, Object

OUTPUT_DIR = Path("./docs")


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


def resolve_alias(member: Alias | Object):
    while isinstance(member, Alias):
        try:
            member = member.target
        except AliasResolutionError:
            return None
    return member


def is_defined_in_module(member: Object | Alias, mod: Module) -> bool:
    member = resolve_alias(member)
    if member is None:
        return False
    return getattr(member, "path", "").startswith(mod.path)


def sanitize_filename(name: str) -> str:
    return name.replace(".", "_")


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
    summary = ""
    if body:
        summary = body.splitlines()[0].strip()

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


def is_public_function(fn: Function) -> bool:
    if fn.name == "__init__":
        return True
    return not fn.name.startswith("_")


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


def render_parameters_table(fn: Function) -> str:
    rows: list[str] = []
    for param in fn.parameters:
        if param.name in {"self", "cls", "/", "*"}:
            continue
        param_name = f"`{param.name}`"
        param_type = f"`{escape_table_cell(as_text(param.annotation))}`"
        rows.append(f"| {param_name} | {param_type} |")
    if not rows:
        return ""
    out = [
        "**Parameters**",
        "",
        "| Parameter | Type |",
        "| ------ | ------ |",
        *rows,
    ]
    return "\n".join(out)


def render_returns(fn: Function, docs: ParsedDoc) -> str:
    yields_desc = docs.yields
    returns_desc = docs.returns
    if yields_desc:
        lines = ["**Yields**", "", f"`{as_text(fn.returns)}`"]
        if yields_desc:
            lines.extend(["", yields_desc])
        return "\n".join(lines)
    if fn.returns is None and not returns_desc:
        return ""
    lines = ["**Returns**", "", f"`{as_text(fn.returns)}`"]
    if returns_desc:
        lines.extend(["", returns_desc])
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

    parameters = render_parameters_table(fn)
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
    parameters = render_parameters_table(constructor)
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
    rows: list[str] = []

    for member in cls.members.values():
        resolved = resolve_alias(member)
        if not isinstance(resolved, Attribute):
            continue
        if not is_public_attribute(resolved):
            continue
        prop_name = f"`{resolved.name}`"
        prop_type = f"`{escape_table_cell(as_text(getattr(resolved, 'annotation', None)))}`"
        rows.append(f"| {prop_name} | {prop_type} |")

    for member in cls.members.values():
        resolved = resolve_alias(member)
        if not isinstance(resolved, Function):
            continue
        if not is_public_function(resolved):
            continue
        if not is_property_method(resolved):
            continue
        prop_name = f"`{resolved.name}`"
        prop_type = f"`{escape_table_cell(as_text(resolved.returns))}`"
        rows.append(f"| {prop_name} | {prop_type} |")

    if not rows:
        return ""

    lines = [
        f'<a id="{class_slug}-properties"></a>',
        "",
        "### Properties",
        "",
        "| Property | Type |",
        "| ------ | ------ |",
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
    parameters = render_parameters_table(fn)
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


def get_documented_members(mod: Module) -> tuple[list[Class], list[Function]]:
    classes: list[Class] = []
    functions: list[Function] = []
    for member in mod.members.values():
        resolved = resolve_alias(member)
        if resolved is None:
            continue
        if not is_defined_in_module(resolved, mod):
            continue
        if isinstance(resolved, Class) and not resolved.name.startswith("_"):
            classes.append(resolved)
        elif isinstance(resolved, Function) and not resolved.name.startswith("_"):
            functions.append(resolved)
    return classes, functions


def frontmatter_for_module(mod: Module, classes: list[Class], functions: list[Function]) -> str:
    module_docs = get_parsed_doc(mod)
    description = module_docs.summary
    if not description and classes:
        description = get_parsed_doc(classes[0]).summary
    if not description:
        description = f"Soniox Python SDK — {mod.path} Reference"
    keywords = [*sorted({cls.name for cls in classes}), *sorted({fn.name for fn in functions})]
    keyword_text = ", ".join(keywords)
    return (
        "---\n"
        f'title: "{mod.path}"\n'
        f'description: "{description}"\n'
        f'keywords: "{keyword_text}"\n'
        "---"
    )


def module_output_path(mod: Module, base_path: Path) -> Path:
    parts = mod.path.split(".")
    if mod.modules:
        folder_path = base_path.joinpath(*parts)
        folder_path.mkdir(parents=True, exist_ok=True)
        return folder_path / "__init__.md"
    folder_path = base_path.joinpath(*parts[:-1])
    folder_path.mkdir(parents=True, exist_ok=True)
    if len(parts) > 1:
        file_name = sanitize_filename(".".join(parts[-2:])) + ".md"
    else:
        file_name = f"{parts[-1]}.md"
    return folder_path / file_name


def write_module_docs(mod: Module, base_path: Path) -> None:
    file_path = module_output_path(mod, base_path)
    classes, functions = get_documented_members(mod)
    module_docs = get_parsed_doc(mod)

    chunks: list[str] = [frontmatter_for_module(mod, classes, functions)]
    if module_docs.body:
        chunks.append(module_docs.body)

    for cls in classes:
        chunks.append(render_class(cls))

    for fn in functions:
        chunks.append(render_module_function(fn))

    content = "\n\n---\n\n".join(chunk for chunk in chunks if chunk.strip())
    file_path.write_text(content, encoding="utf-8")
    print(f"Written {file_path}")

    for sub in mod.modules.values():
        write_module_docs(sub, base_path)


def main() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True, parents=True)
    loader = GriffeLoader(search_paths=["./src", "../src"])
    soniox_module = loader.load("soniox")
    write_module_docs(soniox_module, OUTPUT_DIR)


if __name__ == "__main__":
    main()
