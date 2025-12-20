# File: tests/test_cli.py
"""
Tests for the Command Line Interface (CLI).

Verifies argument parsing, exit codes, and integration with the core processing logic.
"""

from __future__ import annotations
import pytest
from pathlib import Path
from unittest.mock import patch
from context_headers.cli import run


def test_cli_help(capsys: pytest.CaptureFixture[str]) -> None:
    """Test that --help exits with code 0 and prints usage."""
    # argparse exits on help, so we still need catches, but we call run()
    with pytest.raises(SystemExit) as e:
        run(["--help"])
    assert e.value.code == 0

    # NEW: Verify help text is actually printed
    captured = capsys.readouterr()
    # Argparse usually prints to stdout, but can vary based on version/error
    assert "usage: " in captured.out or "usage: " in captured.err


def test_cli_no_files() -> None:
    """Test that running with no files returns 0."""
    assert run([]) == 0


def test_cli_with_changes(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """Test that identifying a file needing a fix returns 1."""
    f = tmp_path / "change.py"
    f.write_text("print('change')", encoding="utf-8")

    # Run in fix mode
    ret = run(["--fix", str(f)])
    assert ret == 1

    # Check output
    out = capsys.readouterr().out
    assert "updated with headers" in out
    assert f.read_text(encoding="utf-8").startswith("# File:")


def test_cli_check_mode_failure(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Test that check mode returns 1 if files need changes."""
    f = tmp_path / "checkfail.py"
    f.write_text("print('fail')", encoding="utf-8")

    ret = run([str(f)])
    assert ret == 1

    out = capsys.readouterr().out
    assert "Missing or incorrect header" in out


def test_main_entry_point() -> None:
    """Test the main entry point calls run and exits."""
    with patch("context_headers.cli.run") as mock_run, patch("sys.exit") as mock_exit:
        mock_run.return_value = 0
        from context_headers.cli import main

        main()
        mock_exit.assert_called_with(0)


def test_main_module_import() -> None:
    """Verifies that the __main__ module can be imported.

    This ensures that the top-level import statements in src/context_headers/__main__.py
    are covered by tests, removing the need for 'pragma: no cover'.
    """
    import context_headers.__main__  # noqa: F401
