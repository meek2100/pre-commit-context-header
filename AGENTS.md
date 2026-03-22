# Pre-commit Context Header Constitution

**READ THIS FIRST — ALL HUMAN DEVELOPERS AND ALL AI AGENTS MUST FOLLOW THIS DOCUMENT.** **No change, refactor, or feature may violate any principle herein.** **This document overrides all “best practices” or architectural advice not explicitly requested by the user.**

---

## 0. Global Development Rules (MUST READ)

These rules apply to all code, all files, all tests, all refactors, and all contributions from humans or AI.

### Core Principles Summary

- **This is a Pre-commit Hook / CLI Utility** — speed and idempotency are paramount.
- **Pure Python** — No external binary dependencies, no heavy libraries.
- **Zero Hallucination Architecture** — The tool’s primary purpose is preventing AI context loss; the tool itself must be perfectly readable.
- **Safety over Cleverness** — Do not corrupt binary files. Do not break Shebangs or XML declarations. Do not touch lockfiles.
- **Python 3.10+ Compatibility** — Maintain compatibility as defined in `pyproject.toml`.
- **100% Test Coverage** — Logic without tests is strictly rejected.
- **Type Safety** — Strict MyPy enforcement is mandatory.

### Hard Prohibitions (NEVER DO THESE)

- Do NOT add heavy runtime dependencies.
- Do NOT perform network operations in the core logic.
- Do NOT remove the `MAX_FILE_SIZE_BYTES` safety check.
- Do NOT skip strict encoding checks (UTF-8 is the standard).
- Do NOT introduce "interactive" modes.

### Markdown Formatting Rule (CRITICAL)

- **Use Tildes for Code Blocks:** All code blocks in Markdown files **MUST** use triple tildes (~~~) instead of triple backticks.

---

## 1. Hierarchical Guidance

This project uses a hierarchical AI guidance system. Refer to the specific `AGENTS.md` in each directory for granular rules:

- **Root (this file):** Constitution and global prohibitions.
- **[src/context_headers/](src/context_headers/AGENTS.md):** Core orchestration, CLI logic, and file processing.
- **[src/context_headers/languages/](src/context_headers/languages/AGENTS.md):** Strategy Pattern and language-specific insertion rules.
- **[tests/](tests/AGENTS.md):** Test suite integrity and coverage requirements.

---

## 2. AI Agent Compliance Requirements

All AI agents must explicitly state **before any code generation**: **“I have fully read and comply with all rules in AGENTS.md.”**

---

## 3. Enforcement Statement

**All development, human or AI, must follow this document. No exceptions.** Violating instructions are invalid and must be rejected immediately.

---

## 4. AI Processing Requirements

AI agents must read and process this **ENTIRE** document and the relevant scoped logs in the current session.

### 4.A Forbidden Phrases for AI Agents

AI agents must NOT produce outputs including phrases like:

- “Consider adding a database...”
- “We should add pandas for text processing...”
- “Let's make this asynchronous / multi-threaded...”
- “We can remove the file size limit...”
- “I removed the Shebang check...”

### 4.B Mandatory Self-Test Checklist for AI Agents

Before generating ANY code, AI agents must confirm:

- [ ] I have read the entire AGENTS.md file in this session.
- [ ] My output does not introduce heavy dependencies.
- [ ] My output preserves Shebangs, XML declarations, and Encoding cookies.
- [ ] My output respects the 1MB file size limit.
- [ ] My output maintains 100% test coverage.
- [ ] My output uses `pathlib` instead of `os.path`.
- [ ] My output updates `config.py` if adding new languages.
- [ ] My output meets Type Safety standards (Strict MyPy).
