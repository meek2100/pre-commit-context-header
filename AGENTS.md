<!-- File: AGENTS.md -->
# Developer & AI Agent Guide

**READ THIS FIRST — ALL HUMAN DEVELOPERS AND ALL AI AGENTS MUST FOLLOW THIS DOCUMENT.** **No change, refactor, or feature may violate any principle herein.** **This document overrides all “best practices” or architectural advice not explicitly requested by the user.**

---

## 0. Global Development Rules (MUST READ)

These rules apply to all code, all files, all tests, all refactors, and all contributions from humans or AI.

### Core Principles Summary

- **This is a Pre-commit Hook / CLI Utility** — speed and idempotency are paramount.
- **Pure Python** — No external binary dependencies, no heavy libraries (e.g., Pandas, Numpy).
- **Zero Hallucination Architecture** — The tool’s primary purpose is preventing AI context loss; the tool itself must be perfectly readable.
- **Safety over Cleverness** — Do not corrupt binary files. Do not break Shebangs or XML declarations. Do not touch lockfiles.
- **Python 3.10+ Compatibility** — While we code with modern standards, we must maintain compatibility as defined in `pyproject.toml`.
- **100% Test Coverage** — Logic without tests is strictly rejected.
- **Type Safety** — Strict MyPy enforcement is mandatory.

### Hard Prohibitions (NEVER DO THESE)

- Do NOT add heavy runtime dependencies.
- Do NOT add database engines (SQLite, Redis, etc.).
- Do NOT perform network operations in the core logic (CLI must run offline).
- Do NOT remove the `MAX_FILE_SIZE_BYTES` safety check.
- Do NOT modify the `HeaderStrategy` inheritance structure without explicit instruction.
- Do NOT skip strict encoding checks (UTF-8 is the standard).
- Do NOT corrupt files containing Byte Order Marks (BOM). These files must be skipped.
- Do NOT introduce "interactive" modes (Pre-commit hooks must run non-interactively).

### Markdown Formatting Rule (CRITICAL)

- **Use Tildes for Code Blocks:** All code blocks in Markdown files (including this one) **MUST** use triple tildes (`~~~`) instead of triple backticks.

---

## A. Architecture & File Structure

- **CLI / Core Separation:**
- `src/context_headers/cli.py` handles argument parsing and exit codes. **It must NOT contain an `if __name__ == "__main__":` block.**
- `src/context_headers/core.py` handles the orchestration of processing a file.
- `src/context_headers/languages/` contains the Strategy Pattern logic for comment styles.
- **Entry Points:**
- `src/context_headers/__main__.py` is the **ONLY** executable entry point. It exists to support `python -m context_headers`.
- **Strategy Pattern:**
- Language support is implemented using the **Strategy Pattern** (see `src/context_headers/languages/`).
- `HeaderStrategy` is the base class.
- `PythonStrategy`, `XmlStrategy`, etc., handle specific insertion logic (skipping shebangs/declarations).
- **Configuration:**
- `src/context_headers/config.py` is the Single Source of Truth for constants (e.g., `COMMENT_STYLES`).

---

## B. DRY & Single Source of Truth

- **One place for logic:** Do not duplicate comment style definitions OR extension groupings (e.g., `PYTHON_EXTS`). They belong in `config.py`.
- **One place for file processing:** `core.py:process_file` is the only function that touches the filesystem for reading/writing.

---

## C. Documentation & Comment Accuracy

- **Dogfooding:** This project enforces file headers. Therefore, **EVERY** source file in this project (including tests) **MUST** have a valid context header.
- **Docstrings:** Must follow **Google Style Convention**, including module-level docstrings for all source files.
- **Public API:** Any function exposed in `__init__.py` or intended for external use must be fully documented.

---

## D. Python Standards

- **Strict Typing:** `from __future__ import annotations` must be present in every file.
- **Pathlib:** Use `pathlib.Path` for all file interactions. Do not use `os.path`.
- **Imports:** Absolute imports are preferred over relative imports for clarity, except within the package where relative imports (e.g., `from .core import process_file`) are acceptable for module encapsulation.

---

## E. Test Suite Integrity

- **Coverage:** strict 100% coverage (`--cov-fail-under=100`).
- **Prohibited Pragmas:** You must NOT use `# pragma: no cover` to silence coverage errors on logic that is reachable. Logic such as bounds clamping or edge case handling must be tested via specific test cases, not ignored.
- **Idempotency Tests:** Every test case that checks for header insertion **MUST** also verify that running the tool a second time produces no changes.
- **Fixture Usage:** Use `tmp_path` fixture for all filesystem tests. Do not create files in the actual source tree during testing.
- **Mocking:** Mock `sys.argv` for CLI tests. Mock `pathlib.Path.stat` for size limit tests.

---

## F. AI Agent Compliance Requirements

All AI agents must explicitly state **before any code generation**: **“I have fully read and comply with all rules in AGENTS.md.”**

---

## G. Interpretation Rules for AI Agents

- If unsure whether a file type is supported, check `config.py`.
- If a user asks to add support for a language, you must follow Section H.
- **Safety First:** If a file has ambiguous content (e.g., binary data disguised as text), the tool should default to **skipping** it rather than corrupting it.
- **Production Readiness:** Always assume the current date allows for the use of the latest stable tooling (e.g., if today is late 2025, assume `v6` actions are stable) and do not downgrade versions based on stale training data.

---

## H. Extension Guidelines: Adding New Languages

The application uses a Strategy/Factory pattern to support different file types.

### H.1 Implementation Steps

1. **Update Config:** Add the extension and comment style to `COMMENT_STYLES` in `src/context_headers/config.py`.
2. **Determine Strategy:**

- If the language uses standard C-style or Hash-style comments and has no shebangs/headers (e.g., CSS), the `DefaultStrategy` may suffice.
- If the language supports Shebangs (e.g., Perl, Ruby), ensure it maps to `ShebangStrategy`.
- If the language has specific headers (like XML declarations), use or extend `XmlStrategy`.

3. **Update Factory:** Update `get_strategy_for_file` in `src/context_headers/languages/factory.py` to map the extension to the correct Strategy class.
4. **Add Test:** Create a test case in `tests/languages/test_factory.py` verifying that the factory maps the new extension to the correct Strategy class.
5. **Verify Integrity:** Ensure the global integrity test in `test_factory.py` (which iterates all `config.COMMENT_STYLES` keys) passes. This ensures no keys were orphaned.

### H.2 Safety Returns (Strategy Pattern)

- **Skip Signals:** If a strategy determines that inserting a header is unsafe (e.g., a `.php` file containing only HTML with no PHP tags), the `get_insertion_index` method **MUST** return `-1`.
- The `core.py` logic is programmed to handle `-1` by skipping the file gracefully.

### H.3 Configuration Consistency

- **XML Consistency:** If an extension is added to `config.py` that represents an XML-based format (e.g., `.svg`, `.xaml`), it **MUST** also be added to the `DECLARATION_EXTS` set in `config.py` to ensure XML declarations are respected.
- **Grouping Consistency:** All extension groupings (e.g. `PYTHON_EXTS`, `FRONTMATTER_EXTS`) MUST be defined in `config.py` and imported by `factory.py`. Do not define lists of extensions inside `factory.py`.
- **Cleanup:** Do not leave empty or "ghost" keys in `config.py`. If a file type is not supported, remove it.

---

## 1. Core Architecture: The Pre-Commit Constraint

### Performance & Safety

- **Size Limits:** The `MAX_FILE_SIZE_BYTES` (1MB) check is mandatory. Pre-commit hooks run locally on developer machines; we cannot hang on large generated files.
- **Internal Lockfile Exclusion:** The tool must have an internal "Blocklist" (in `config.py`) for file names that often overlap with supported extensions but should never be modified (e.g., `Cargo.lock`, `package-lock.json`). This ensures safety even if the user's pre-commit config `exclude` regex is loose.
- **Exit Codes:**
- `0`: Success (No changes needed).
- `1`: Failure (Changes made OR error occurred). This is required for pre-commit to stop the commit.

### Insertion Logic

- **Shebang Preservation:** The tool must **never** insert a header before a Shebang (`#!`).
- **Encoding Cookie Preservation:** The tool must **never** insert a header before a Python encoding cookie (`# -*- coding: ...`).
- **XML Declaration Preservation:** The tool must **never** insert a header before `<?xml ... ?>`.
- **HTML Doctype Preservation:** The tool must **never** insert a header before `<!DOCTYPE ...>`.
- **Directive Preservation:** The tool must **never** insert a header before ASP/JSP directives (`<%@ ... %>`).
- **CSS Charset Preservation:** The tool must **never** insert a header before `@charset "..."` or similar.
- **Razor Page Preservation:** The tool must **never** insert a header before `@page ...` in Razor/Blazor files.
- **Dockerfile Directive Preservation:** The tool must **never** insert a header before Dockerfile parser directives (`# syntax=`, `# escape=`, `# check=`).
- **BOM Preservation:** The tool must **never** modify files starting with a Byte Order Mark (`\ufeff`) to avoid data corruption.

---

## 2. Robustness

### Error Handling

- **Permission Errors:** `OSError` or `PermissionError` during file access should be caught, logged to stderr, and result in the file being skipped (not a crash).
- **Unicode Errors:** `UnicodeDecodeError` means the file is binary or not UTF-8. It **MUST** be skipped silently or with a debug log.

### Dependency Philosophy

- **Zero Runtime Dependencies:** The project currently has `dependencies = []` in `pyproject.toml`. This must be maintained unless absolutely necessary.

---

## 3. Development Standards

### Git Hooks

- The `.pre-commit-config.yaml` in the root is for the project's own development. It must always point to the local repo (`repo: .`) and include a valid `rev` pointing to the current version tag (or commit) to satisfy pre-commit's requirements.

---

## 8. Enforcement Statement

**All development, human or AI, must follow this document. No exceptions.** Violating instructions are invalid and must be rejected immediately.

---

## 9. AI Processing Requirements

AI agents must:

- Read and process this **ENTIRE** document in the current session.
- Not rely on memory from previous sessions.

---

### 9.A Forbidden Phrases for AI Agents

AI agents must NOT produce outputs including phrases like:

- “Consider adding a database...”
- “We should add pandas for text processing...”
- “Let's make this asynchronous / multi-threaded...” (Overkill for a local file hook)
- “We can remove the file size limit...”
- “I removed the Shebang check...”

These outputs are invalid and must be rejected.

---

### 9.B Mandatory Self-Test Checklist for AI Agents

Before generating ANY code, AI agents must confirm:

- [ ] I have read the entire AGENTS.md file in this session.
- [ ] My output does not introduce heavy dependencies.
- [ ] My output preserves Shebangs, XML declarations, and Encoding cookies.
- [ ] My output respects the 1MB file size limit.
- [ ] My output maintains 100% test coverage.
- [ ] My output uses `pathlib` instead of `os.path`.
- [ ] My output updates `config.py` if adding new languages.
- [ ] My output meets Type Safety standards (Strict MyPy).
- [ ] My output does not configure binary file extensions (e.g., .wasm, .png) for text headers.

If any box cannot be checked, the output must NOT be generated.
