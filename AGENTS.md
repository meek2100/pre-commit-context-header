<!-- File: AGENTS.md -->
# Pre-commit Context Header Constitution

Universal pre-commit hook and CLI utility that enforces file path context banners to prevent AI context loss. Speed, idempotency, and safety are paramount.

---

## 1. Role & Tech Stack

- **Persona:** Senior Tooling Engineer focused on zero technical debt, pure Python performance, and safety.
- **Runtime:** Pure Python (`>=3.10`), strictly zero external runtime dependencies (`dependencies = []`).
- **Toolchain:** `uv` for local environment management, testing, and distribution packaging.
- **Quality Standards:** 100% test coverage mandatory (`--cov-fail-under=100`), strict MyPy, strict Pyright, and Ruff.

---

## 2. Key Commands

~~~bash
# Synchronize environment and dev dependencies
uv sync

# Run the complete test suite (enforces 100% coverage)
uv run pytest

# Run a specific test file or targeted test case
uv run pytest tests/test_core.py -k <test_name>

# Linting and formatting checks
uv run ruff check .
uv run ruff format --check .

# Auto-fix linting and format code
uv run ruff check --fix .
uv run ruff format .

# Strict type checking
uv run mypy .
uv run pyright

# Run all pre-commit hooks locally
SKIP=no-commit-to-branch uv run pre-commit run --all-files

# Build distribution packages (sdist and wheel)
uv build
~~~

---

## 3. Boundaries & Guardrails

### Always
- **Pathlib:** Use `pathlib.Path` for all file interactions; never use `os.path`.
- **Strict Typing:** Ensure `from __future__ import annotations` is at the top of every Python source file.
- **Coverage & Quality:** Verify that `uv run pytest` maintains 100% statement coverage before concluding any task.
- **Context Header Rule:** Every source and test file must feature a valid top-level context header (`# File: ...`).
- **Markdown Code Fences:** All code blocks in Markdown files **MUST** use triple tildes (`~~~`) instead of triple backticks.
- **Configuration Sync:** Explicitly duplicate `ALWAYS_SKIP_FILENAMES` from `config.py` into `.pre-commit-hooks.yaml:exclude`.

### Ask First
- Adding new language strategies or altering existing parsing mechanisms.
- Modifying GitHub Actions workflows, release pipelines, or build configuration.
- Proposing changes to file size thresholds or default exclusion lists.

### Never
- Never add heavy or external runtime dependencies (`dependencies = []` must remain empty).
- Never execute network requests or async runtime dependencies in core logic.
- Never remove or bypass the `MAX_FILE_SIZE_BYTES` safety check (1MB threshold).
- Never break Shebangs (`#!`), Python encoding cookies (`# -*- coding:`), XML declarations (`<?xml`), HTML doctypes (`<!DOCTYPE`), CSS `@charset`, or Dockerfile directives (`# syntax=`).
- Never touch recognized lockfiles, binary files, or files with UTF-8 BOM (`\ufeff`).
- Never introduce interactive CLI prompts (the hook must execute completely unattended).

---

## 4. Hierarchical Guidance

Refer to directory-scoped documentation for granular implementation rules:

- **[src/context_headers/](src/context_headers/AGENTS.md):** Core orchestration, CLI argument parsing, and `process_file` DRY rules.
- **[src/context_headers/languages/](src/context_headers/languages/AGENTS.md):** Strategy Pattern implementation and language-specific insertion safety.
- **[tests/](tests/AGENTS.md):** Test suite integrity, mocking conventions, and idempotency tests.
