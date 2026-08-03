# File: tests/test_version.py
"""
Tests for package version single-sourcing.

`__version__` in `src/context_headers/__init__.py` is the ONLY place the version
is written. `pyproject.toml` derives it via `[tool.setuptools.dynamic]`, so the
two cannot drift. These tests guard that arrangement rather than compare copies.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from context_headers import __version__

PYPROJECT = Path(__file__).parents[1] / "pyproject.toml"


def test_version_is_a_sane_string() -> None:
    """__version__ must look like a release version."""
    assert re.fullmatch(r"\d+\.\d+\.\d+([.-]\w+)*", __version__), __version__


def test_pyproject_does_not_duplicate_the_version() -> None:
    """pyproject must DERIVE the version, never restate it.

    Regression guard for the drift this replaced: pyproject said 0.1.1 while
    __version__ said 0.1.0, and the release shipped with two different answers.
    """
    content = PYPROJECT.read_text(encoding="utf-8")
    assert 'dynamic = ["version"]' in content, "pyproject must declare a dynamic version"
    assert 'attr = "context_headers.__version__"' in content, (
        "pyproject must resolve the version from context_headers.__version__"
    )
    literal = re.search(r"^\s*version\s*=\s*[\"']", content, re.MULTILINE)
    assert literal is None, (
        "pyproject.toml contains a literal `version = \"...\"`. It will drift from "
        "__version__. Remove it and let [tool.setuptools.dynamic] resolve it."
    )


def test_built_metadata_matches_source() -> None:
    """When installed, the built distribution's version must equal __version__.

    This is what actually proves the dynamic wiring worked — the config test
    above only proves it is declared.
    """
    from importlib.metadata import PackageNotFoundError, version

    try:
        installed = version("pre-commit-context-header")
    except PackageNotFoundError:
        pytest.skip("package not installed; running from the source tree")
    assert installed == __version__
