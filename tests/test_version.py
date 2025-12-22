# File: tests/test_version.py
"""
Tests for package version consistency.

Ensures the version defined in `__init__.py` matches `pyproject.toml`.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

from context_headers import __version__


def test_version_matches_pyproject() -> None:
    """Verifies that the package __version__ matches pyproject.toml.

    This ensures that the released package version is always in sync
    with the installed package version.
    """
    pyproject_path = Path(__file__).parents[1] / "pyproject.toml"

    # Use modern standard library (tomllib) if available (Python 3.11+),
    # otherwise fall back to regex for Python 3.10.
    if sys.version_info >= (3, 11):
        import tomllib

        with pyproject_path.open("rb") as f:
            data = tomllib.load(f)
            expected_version = data["project"]["version"]
    else:
        # Robustness: Matches both "version = '...'" and 'version = "..."'
        content = pyproject_path.read_text(encoding="utf-8")
        match = re.search(r'^version\s*=\s*["\'](.*?)["\']', content, re.MULTILINE)

        assert match is not None, "Could not find version key in pyproject.toml"
        expected_version = match.group(1)

    assert __version__ == expected_version
