# File: tests/test_config_sync.py
"""
Tests for configuration synchronization.

Verifies that the pre-commit hooks configuration matches the internal
Python configuration (Single Source of Truth enforcement).
"""

from __future__ import annotations
from pathlib import Path
from context_headers.config import ALWAYS_SKIP_FILENAMES


def test_hooks_yaml_matches_config_exclusions() -> None:
    """Verifies that .pre-commit-hooks.yaml excludes all files in ALWAYS_SKIP_FILENAMES.

    The pre-commit hook definition contains a regex 'exclude' field that must
    mirror the internal Python set to ensure performance optimization.
    """
    hooks_path = Path(__file__).parents[1] / ".pre-commit-hooks.yaml"
    content = hooks_path.read_text(encoding="utf-8")

    # The exclusion list in the YAML is a regex. Filenames typically have dots escaped.
    # We verify that every filename in the config python set appears in the YAML.
    # To be robust, we escape the filename for regex matching (handling the dot).

    for filename in ALWAYS_SKIP_FILENAMES:
        # In the regex inside YAML, 'package-lock.json' is likely written as 'package-lock\.json'.
        # We construct the expected pattern:
        expected_pattern = filename.replace(".", r"\.")

        # We ensure this pattern exists in the file content.
        assert expected_pattern in content, (
            f"Filename '{filename}' from config.py is missing in .pre-commit-hooks.yaml exclude list. "
            f"Expected pattern '{expected_pattern}' not found."
        )
