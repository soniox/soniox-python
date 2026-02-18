from pathlib import Path

from griffe import AliasResolutionError, Class, Function, GriffeLoader, Module
from griffe._internal.models import Alias, Object


def render_function(fn: Function) -> str:
    md: list[str] = []
    md.append(f"### `{fn.name}`")

    if fn.docstring:
        md.append(fn.docstring.value.strip())

    md.append("#### Signature")
    md.append(f"```python\n{fn.signature()}\n```")

    if fn.parameters:
        md.append("#### Parameters")
        for param in fn.parameters:
            desc = ""
            if fn.docstring and fn.docstring.parsed:
                for section in fn.docstring.parsed:
                    if section.kind == "parameters":
                        for p in section.value:
                            if p.name == param.name:
                                desc = p.description
            md.append(f"- **{param.name}** ({param.annotation}): {desc}")

    if fn.returns:
        md.append("#### Returns")
        md.append(str(fn.returns))

    return "\n\n".join(md)


def render_class(cls: Class) -> str:
    md: list[str] = []
    md.append(f"## Class `{cls.name}`")

    if cls.docstring:
        md.append(cls.docstring.value.strip())

    attrs = [m for m in cls.members.values() if m.kind == "attribute"]

    if attrs:
        md.append("### Attributes")
        for attr in attrs:
            md.append(f"- **{attr.name}**: {attr.docstring.value if attr.docstring else ''}")

    methods = [m for m in cls.members.values() if m.kind == "function"]

    for method in methods:
        md.append(render_function(method))

    return "\n\n".join(md)


def resolve_alias(member: Alias | Object):
    while isinstance(member, Alias):
        try:
            member = member.target
        except AliasResolutionError:
            return None
    return member


def render_module(mod: Module):
    md: list[str] = []

    if mod.docstring:
        md.append(mod.docstring.value.strip())

    for member in mod.members.values():
        member = resolve_alias(member)
        if isinstance(member, Class):
            md.append(render_class(member))
        elif isinstance(member, Function):
            md.append(render_function(member))

    return "\n\n---\n\n".join(md)


def is_defined_in_module(member: Object | Alias, mod: Module) -> bool:
    member = resolve_alias(member)
    if member is None:
        return False
    return getattr(member, "path", "").startswith(mod.path)


def sanitize_filename(name: str) -> str:
    return name.replace(".", "_")


def write_module_docs(mod: Module, base_path: Path):
    parts = mod.path.split(".")

    if mod.modules:  # package with submodules
        folder_path = base_path.joinpath(*parts)
        folder_path.mkdir(parents=True, exist_ok=True)
        file_path = folder_path / "__init__.md"
    else:
        folder_path = base_path.joinpath(*parts[:-1])
        folder_path.mkdir(parents=True, exist_ok=True)
        if len(parts) > 1:
            file_name = sanitize_filename(".".join(parts[-2:])) + ".md"
        else:
            file_name = f"{parts[-1]}.md"
        file_path = folder_path / file_name

    frontmatter = f"""---
title: {mod.path}
description: {mod.docstring.value.strip().splitlines()[0] if mod.docstring else f"Description for {mod.name}"}
keywords: {", ".join(list(mod.members.keys()))}
---
"""
    md_lines = [frontmatter]
    if mod.docstring:
        md_lines.append(mod.docstring.value.strip())

    for member in mod.members.values():
        member = resolve_alias(member)
        if member is None:
            continue
        if not is_defined_in_module(member, mod):
            continue
        if isinstance(member, Class):
            md_lines.append(render_class(member))
        elif isinstance(member, Function):
            md_lines.append(render_function(member))

    content = "\n\n---\n\n".join(md_lines)
    file_path.write_text(content, encoding="utf-8")
    print(f"Written {file_path}")

    for sub in mod.modules.values():
        write_module_docs(sub, base_path)


OUTPUT_DIR = Path("./docs")
OUTPUT_DIR.mkdir(exist_ok=True, parents=True)

loader = GriffeLoader(search_paths=["./src", "../src"])
soniox_module = loader.load("soniox")
write_module_docs(soniox_module, OUTPUT_DIR)
