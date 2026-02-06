from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from sphinx.application import Sphinx

CLASS_RE = re.compile(r"^(#{3,}) class ([\w.]+)\((.*?)\)$", re.MULTILINE)
BRACES_RE = re.compile(r"\{[^}{]+\}")
PARAMS_RE = re.compile(r"\n\* \*\*Parameters:\*\*[\s\S]*?(?=\n\S|\Z)")


def wrap_braces(match: re.Match[str]) -> str:
    value = match.group(0)
    if "`" in value:
        return value
    return f"`{value}`"


def remove_everything_until_first_h2(text: str) -> str:
    lines = text.split("\n")
    for i, line in enumerate(lines):
        if not line:
            continue
        if line.startswith("##"):
            return "\n".join(lines[i:])

    return text


def insert_fumadocs_frontmatter(text: str, path: Path) -> str:
    path_to_title = {
        "index.md": "Full reference",
        "async.md": "Async Soniox client",
        "core.md": "Core",
        "sync.md": "Soniox client",
        "types.md": "Types",
    }
    frontmatter = f"---\ntitle: {path_to_title.get(path.name, path.name)}\n---\n\n"
    return f"{frontmatter}{text}"


def extract_class_name(text: str) -> str:
    def get_class_name(class_line: str):
        end = class_line.find("(")
        if end == -1:
            end = len(class_line)
        # Take the last dotted segment
        return class_line[:end].split(".")[-1]

    def get_class_definition(class_line: str, class_name: str):
        start = class_line.find(class_name)
        return class_line[start:]

    lines = text.split("\n")
    for i, line in enumerate(lines):
        if not line:
            continue
        if line.startswith("### *class*"):
            class_name = get_class_name(line)
            class_definiton = get_class_definition(line, class_name)
            lines[i] = f"### {class_name}\n ```python {class_definiton}```\n"

    return "\n".join(lines)


def extract_parameters1(text: str) -> str:
    def get_return_type():
        pass

    chunks = text.split("\n\n")
    for i, chunk in enumerate(chunks):
        if not chunk:
            continue
        if chunk.startswith("* **Parameters:**"):
            parameters = chunk.split("\n")[1:]
            return_type = list(filter(lambda p: p.startswith("* **Return type:**"), parameters))
            for parameter in parameters:
                print("parameter: ", parameter)
                print("return_type: ", return_type)

    return text


def extract_parameters2(text: str) -> str:
    # extract params from bullet point (with aditional link)
    # get extra docstring
    # remove everything until ### or ##
    # create nice params with links

    def find_h2_or_h3(lines: list[str], start: int = 0) -> int:
        for i, line in enumerate(lines[start:]):
            if line.startswith("## ") or line.startswith("### "):
                return i + start
        return -1

    @dataclass
    class ParsedParamter:
        name: str
        type: str
        description: str | None = None
        link: str | None = None
        links: list[str] | None = None

    def parse_parameters(lines: list[str], start: int, end: int):
        parameters: dict[str, ParsedParamter]
        for line in lines[start:end]:
            stripped = line.strip()
            if stripped.startswith("* **Return type:**"):
                return_type = line[len("* **Return type:**") :].strip()
                pass
            else:
                is_extra_info = stripped.startswith("#### ")
                parameter = stripped.replace("*", "").split(" ")
                print("parameter: ", parameter)
                pass

        # print("params: ", lines[start:end], start, end)
        #
        pass

    to_change: list[tuple[tuple[int, int], str]] = []
    lines = text.split("\n")
    for i, line in enumerate(lines):
        if not line:
            continue

        if line.startswith("* **Parameters:**"):
            start = i
            end = find_h2_or_h3(lines, start + 1)
            parse_parameters(lines, start + 1, end)
            to_change.append(((start, end), ""))

    for (start, end), new_text in reversed(to_change):
        lines[start:end] = new_text

    return text
    return "\n".join(lines)


def sanitize_md_content(text: str, path: Path) -> str:
    result = text
    result = remove_everything_until_first_h2(result)
    result = insert_fumadocs_frontmatter(result, path)
    result = extract_class_name(result)
    result = extract_parameters2(result)
    return result


def on_build_finished(app: Sphinx, exception: Exception | None) -> None:
    if exception is not None:
        return
    if app.builder.name != "markdown":
        return
    output_dir = Path(app.outdir)
    for path in output_dir.rglob("*.md"):
        original = path.read_text(encoding="utf-8")
        cleaned = sanitize_md_content(original, path)
        path.write_text(cleaned, encoding="utf-8")


def setup(app: Sphinx) -> dict[str, object]:
    app.connect("build-finished", on_build_finished)
    return {"version": "0.1", "parallel_read_safe": True}
