# File: tests/test_version.py
"""
Tests for package version consistency.

Ensures the version defined in `__init__.py` matches `pyproject.toml`.
"""

from __future__ import annotations

import re
from pathlib import Path

from context_headers import __version__


def test_version_matches_pyproject() -> None:
    """Verifies that the package __version__ matches pyproject.toml.

    This ensures that the released package version is always in sync
    with the installed package version.
    """
    pyproject_path = Path(__file__).parents[1] / "pyproject.toml"
    content = pyproject_path.read_text(encoding="utf-8")

    # We use regex to avoid adding a runtime dependency (tomli/tomllib)
    # just for this single test on older Python versions (3.9/3.10).
    # Robustness: Matches both "version = '...'" and 'version = "..."'
    match = re.search(r'^version\s*=\s*["\'](.*?)["\']', content, re.MULTILINE)

    assert match is not None, "Could not find version key in pyproject.toml"
    expected_version = match.group(1)

    assert __version__ == expected_version
