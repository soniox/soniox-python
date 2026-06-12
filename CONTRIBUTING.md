# Contributing

Contributions are welcome. PRs that are small, typed, and tested move through review fastest.

By participating in this project, you agree to abide by our [Code of Conduct](CODE_OF_CONDUCT.md).

## Development setup

Install [uv](https://docs.astral.sh/uv/) and [just](https://github.com/casey/just), then:

```bash
git clone https://github.com/soniox/soniox-python
cd soniox-python
uv sync --extra dev
```

> Python 3.13.6 has a regression in the `ssl` module that hangs realtime WebSocket sessions ([CPython #137583](https://github.com/python/cpython/issues/137583)). For local development, use Python 3.10 through 3.12, or 3.13.5 / 3.13.7 and later.

Day-to-day commands:

```bash
just test          # full test suite
just lint          # ruff
just typecheck     # pyright
just docs          # regenerate docs/*.md from source
```

## Opening a pull request

Open PRs against the `dev` branch. `main` tracks releases.

Before you push:

1. Keep the PR focused. One bug fix, one feature, or one refactor. Mixed PRs are slower to review.
2. Add tests. New endpoints belong in `tests/unit/`; realtime helpers belong in `tests/realtime/`.
3. Run `just lint`, `just typecheck`, and `just test`. All three must pass before review.
4. Maintain coverage above the threshold set in `pyproject.toml`.
5. Update the `[Unreleased]` section of `CHANGELOG.md` for any user-visible change. Categorize as Added, Changed, Fixed, or Removed.
6. If you changed public APIs, regenerate the reference docs with `just docs`.

To pick up a newer OpenAPI schema, run `just download-schema`. This pulls the latest `openapi.json` into `tests/data/`. The `test_schema_drift.py` suite then reports missing fields and changed signatures automatically.

## Conventions

- `ruff` handles formatting and lint rules; the configuration lives in `pyproject.toml`.
- `pyright` runs in strict mode against `src/`. Tests have a narrower config in the same file.
- Write docstrings in plain markdown with backticks for code references. Do not use Sphinx directives such as `:meth:` or `:param:`. They leak as raw text into the generated reference.
- Write comments to explain why, not what. Well-named identifiers already say what the code does.

## Reporting bugs

File issues at [github.com/soniox/soniox-python/issues](https://github.com/soniox/soniox-python/issues) using the bug report template. Include the SDK version, the Python version, and a minimal reproducer.

## Reporting security issues

Do not file a public issue for security vulnerabilities. See [SECURITY.md](SECURITY.md) for the channels we monitor.
