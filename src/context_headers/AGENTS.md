<!-- File: src/context_headers/AGENTS.md -->
# Core Orchestration & CLI Guidance

This directory contains the central logic for the pre-commit hook. AI agents must follow these rules when modifying CLI or orchestration logic.

---

## 1. Architecture & Module Separation

- **CLI / Core Separation:**
  - `cli.py` handles argument parsing and exit codes. **It must NOT contain an `if __name__ == "__main__":` block.**
  - `core.py` handles the orchestration of processing a file.
- **Entry Points:**
  - `__main__.py` is the **ONLY** executable entry point.
- **Configuration:**
  - `config.py` is the Single Source of Truth for constants.
  - **Configuration Sync:** The `exclude` list in `.pre-commit-hooks.yaml` MUST explicitly duplicate the `ALWAYS_SKIP_FILENAMES` from `config.py`.

---

## 2. File Processing Rules

- **DRY Logic:** `core.py:process_file` is the only function that touches the filesystem for reading/writing.
- **Robustness:**
  - `OSError` or `PermissionError` must be caught, logged to stderr, and result in skipping (not a crash).
  - `UnicodeDecodeError` means the file is binary or not UTF-8; skip it.
- **Size Limits:** Always respect `MAX_FILE_SIZE_BYTES`.

---

## 3. Python Standards

- **Strict Typing:** `from __future__ import annotations` must be present in every file.
- **Public API Exports:** Use `__all__` in `cli.py` and `core.py`.
- **Pathlib:** Use `pathlib.Path` for all file interactions.
- **Docstrings:** Follow Google Style Convention, including module-level docstrings.

---

## 4. Context Header Rule

EVERY source file in this project MUST have a valid context header.

~~~python
# Path: path/to/file.py
~~~
