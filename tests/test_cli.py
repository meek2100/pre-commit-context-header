# File: tests/test_cli.py
"""
Tests for the Command Line Interface (CLI).

Verifies argument parsing, exit codes, and integration with the core processing logic.
"""

from __future__ import annotations
import pytest
import sys
import runpy
from pathlib import Path
from unittest.mock import patch
from context_headers.cli import run


def test_cli_help(capsys: pytest.CaptureFixture[str]) -> None:
    """Test that --help exits with code 0 and prints usage."""
    # argparse exits on help, so we still need catches, but we call run()
    with pytest.raises(SystemExit) as e:
        run(["--help"])
    assert e.value.code == 0

    # Verify help text is actually printed
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


def test_cli_remove_mode(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """Test that --remove successfully removes headers."""
    f = tmp_path / "remove.py"
    f.write_text("# File: ...\nprint('hi')\n", encoding="utf-8")

    ret = run(["--remove", str(f)])
    assert ret == 1

    out = capsys.readouterr().out
    assert "headers removed" in out
    assert f.read_text(encoding="utf-8") == "print('hi')\n"


def test_main_entry_point() -> None:
    """Test the main entry point calls run and exits."""
    with patch("context_headers.cli.run") as mock_run, patch("sys.exit") as mock_exit:
        mock_run.return_value = 0
        from context_headers.cli import main

        main()
        mock_exit.assert_called_with(0)


def test_main_execution() -> None:
    """Verifies __main__.py actually runs main().

    This simulates `python -m context_headers` via runpy to ensure
    the `if __name__ == '__main__':` block in __main__.py is covered.
    """
    # We patch sys.argv to simulate a clean run that exits 0 (help)
    # This prevents the actual run from trying to parse pytest args
    with patch.object(sys, "argv", ["context-headers", "--help"]):
        with pytest.raises(SystemExit) as e:
            runpy.run_module("context_headers", run_name="__main__")
        assert e.value.code == 0


def test_cli_sys_argv_fallback() -> None:
    """Verifies that run() uses sys.argv if no arguments are provided.

    This ensures the default argument `argv=None` in run() is covered.
    """
    # Simulate command line arguments: ['prog_name', '--help']
    # run() (without args) will call parser.parse_args(None), which defaults to sys.argv[1:]
    with patch("sys.argv", ["context-headers", "--help"]):
        with pytest.raises(SystemExit) as e:
            run()
        assert e.value.code == 0
