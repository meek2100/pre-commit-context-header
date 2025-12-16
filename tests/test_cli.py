# File: tests/test_cli.py
from __future__ import annotations
import pytest
import sys
from pathlib import Path
from unittest.mock import patch
from context_headers.cli import main


def test_main_cli_help() -> None:
    """Test that --help exits with code 0."""
    with (
        patch("sys.argv", ["context-headers", "--help"]),
        pytest.raises(SystemExit) as e,
    ):
        main()
    assert e.value.code == 0


def test_main_cli_no_files() -> None:
    """Test that running with no arguments exits with code 0."""
    with patch("sys.argv", ["context-headers"]), pytest.raises(SystemExit) as e:
        main()
    assert e.value.code == 0


def test_main_cli_with_changes(tmp_path: Path) -> None:
    """Test that identifying a file needing a fix exits with code 1."""
    f = tmp_path / "change.py"
    f.write_text("print('change')", encoding="utf-8")

    # Run in fix mode; should update file and exit with 1
    with (
        patch("sys.argv", ["context-headers", "--fix", str(f)]),
        pytest.raises(SystemExit) as e,
    ):
        main()
    assert e.value.code == 1
    assert f.read_text(encoding="utf-8").startswith("# File:")
