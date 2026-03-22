<!-- File: src/context_headers/languages/AGENTS.md -->

# Language Strategy & Extension Guidance

This directory implements the **Strategy Pattern** for language-specific header insertion rules.

---

## 1. Strategy Pattern Rules

- **Base Class:** `HeaderStrategy` is the base class for all language-specific logic.
- **Factory Mapping:** `factory.py:get_strategy_for_file` is the central mapping between file extensions and strategies.
- **Extension Groups:** All extension groupings (e.g., `PYTHON_EXTS`, `XML_EXTS`) MUST be defined in `config.py` and imported here.

---

## 2. Insertion Safety & Preservation

- **Insertion Points:** The `get_insertion_index` method must return `-1` if insertion is unsafe.
- **Preservation Rules:**
  - Never insert before a **Shebang** (`#!`).
  - Never insert before a **Python Encoding Cookie** (`# -*- coding: ...`).
  - Never insert before an **XML Declaration** (`<?xml ... ?>`).
  - Never insert before an **HTML Doctype** (`<!DOCTYPE ...>`).
  - Never insert before **BOM** (`\ufeff`).
  - Never insert before **Dockerfile Parser Directives** (`# syntax=`).

---

## 3. Extension Guidelines: Adding New Languages

1. **Update Config:** Add extension and comment style to `COMMENT_STYLES` in `config.py`.
2. **Assign Strategy:** Map to `DefaultStrategy`, `ShebangStrategy`, `XmlStrategy`, or create a new one if needed.
3. **Update Factory:** Map the extension to the strategy in `factory.py`.
4. **Add Test:** Verify mapping in `tests/languages/test_factory.py`.

---

## 4. Context Header Rule

EVERY source file in this project MUST have a valid context header.

```python
# File: path/to/file.py
```
