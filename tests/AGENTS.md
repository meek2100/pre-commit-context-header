<!-- File: tests/AGENTS.md -->
# Test Suite Integrity & Standards

This directory contains the test suite for the pre-commit hook. AI agents must maintain 100% coverage and follow strict testing patterns.

---

## 1. Coverage Requirements

- **Strict 100% Coverage:** Mandatory coverage check (`--cov-fail-under=100`).
- **No Pragma Overrides:** Do NOT use `# pragma: no cover` to ignore reachable logic.
- **Manual Verification:** If 100% coverage isn't met, you MUST add specific test cases for the missing lines.

---

## 2. Mandatory Test Patterns

- **Idempotency:** Every test case that checks for header insertion MUST also verify that running the tool a second time produces no changes.
- **Configuration Sync:** Ensure external configs (like `.pre-commit-hooks.yaml`) stay in sync with constants in `config.py`.
- **Fixture Usage:** Use `tmp_path` for all filesystem-related tests.
- **Mocking Strategy:**
  - Mock `sys.argv` for CLI integration tests.
  - Mock `pathlib.Path.stat` for file size limit tests.

---

## 3. Formatting & Standards

- **Dogfooding:** EVERY test file in this project MUST have a valid context header.

~~~python
# Path: tests/test_example.py
~~~

- **Style:** Follow Google Style Convention for docstrings.
