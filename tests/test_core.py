# File: tests/test_core.py
"""
Tests for the core file processing logic.

Verifies file reading/writing, strategy application, idempotency,
and safety mechanisms like size limits and binary file skipping.
"""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from context_headers.core import process_file
from context_headers.config import MAX_FILE_SIZE_BYTES


def test_process_file_adds_header(tmp_path: Path) -> None:
    """Verifies that process_file correctly adds a header to a new file."""
    f = tmp_path / "test.py"
    f.write_text("print('hello')\n", encoding="utf-8")

    assert process_file(str(f), fix_mode=True)

    content = f.read_text(encoding="utf-8")
    assert content.startswith(f"# File: {f.as_posix()}\n")


def test_process_file_is_idempotent(tmp_path: Path) -> None:
    """Verifies that running process_file twice does not duplicate headers."""
    f = tmp_path / "repeat.py"
    f.write_text("print('once')\n", encoding="utf-8")

    process_file(str(f), fix_mode=True)
    first_pass = f.read_text()

    assert not process_file(str(f), fix_mode=True)
    assert f.read_text() == first_pass


def test_process_file_large_file_skipped(tmp_path: Path) -> None:
    """Verifies that files exceeding MAX_FILE_SIZE_BYTES are skipped."""
    f = tmp_path / "large.py"
    f.touch()
    with patch("pathlib.Path.stat") as mock_stat:
        mock_stat.return_value.st_size = MAX_FILE_SIZE_BYTES + 1
        assert not process_file(str(f), fix_mode=True)


def test_process_file_no_fix_mode(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Verifies that fix_mode=False reports issues but does not modify files."""
    f = tmp_path / "check.py"
    f.write_text("print('hi')\n")

    assert process_file(str(f), fix_mode=False)
    assert "Missing or incorrect header" in capsys.readouterr().out
    assert f.read_text() == "print('hi')\n"


def test_process_file_binary_skipped(tmp_path: Path) -> None:
    """Verifies that files triggering UnicodeDecodeError are safely skipped."""
    f = tmp_path / "binary.exe"
    f.write_bytes(b"\x80\x81\x82")  # Invalid UTF-8

    # Should return False (skipped)
    assert not process_file(str(f), fix_mode=True)
    # File should remain unchanged
    assert f.read_bytes() == b"\x80\x81\x82"


def test_process_file_bom_skipped(tmp_path: Path) -> None:
    """Verifies that files with a Byte Order Mark (BOM) are skipped to prevent corruption."""
    f = tmp_path / "bom.py"
    # Write BOM + Content
    f.write_text("\ufeffprint('hi')\n", encoding="utf-8")

    # Should return False (skipped)
    assert not process_file(str(f), fix_mode=True)
    # File should remain unchanged (BOM preserved, no header added)
    assert f.read_text(encoding="utf-8") == "\ufeffprint('hi')\n"


def test_process_file_unsupported_extension_skipped(tmp_path: Path) -> None:
    """Verifies that files with unsupported extensions are quietly skipped."""
    f = tmp_path / "test.unknown"
    f.write_text("content", encoding="utf-8")

    # Should return False because get_strategy_for_file returns None
    assert not process_file(str(f), fix_mode=True)
    assert f.read_text(encoding="utf-8") == "content"


def test_process_file_stat_oserror(tmp_path: Path) -> None:
    """Verifies that OSErrors during stat checks are handled gracefully."""
    f = tmp_path / "stat_error.py"
    f.touch()
    with patch("pathlib.Path.stat", side_effect=OSError):
        assert not process_file(str(f), fix_mode=True)


def test_process_file_permission_error(tmp_path: Path) -> None:
    """Verifies that PermissionError during stat checks is handled gracefully."""
    f = tmp_path / "perm_error.py"
    f.touch()
    # PermissionError is a subclass of OSError, but we want to ensure
    # we specifically catch it if logic splits in the future.
    with patch("pathlib.Path.stat", side_effect=PermissionError):
        assert not process_file(str(f), fix_mode=True)


def test_process_file_read_oserror(tmp_path: Path) -> None:
    """Verifies that OSErrors during file reading are handled gracefully."""
    f = tmp_path / "read_error.py"
    f.touch()
    with patch("pathlib.Path.read_text", side_effect=OSError):
        assert not process_file(str(f), fix_mode=True)


def test_process_file_adds_newline_if_missing(tmp_path: Path) -> None:
    """Verifies that a newline is appended to the last line if missing."""
    f = tmp_path / "no_newline.py"
    f.write_text("print('hi')", encoding="utf-8")  # No \n

    assert process_file(str(f), fix_mode=True)

    content = f.read_text(encoding="utf-8")
    assert content.endswith("\n")
    assert content.startswith("# File:")


def test_process_file_already_correct(tmp_path: Path) -> None:
    """Verifies that files with correct headers are left untouched."""
    f = tmp_path / "correct.py"
    header = f"# File: {f.as_posix()}\n"
    f.write_text(header + "print('hi')\n", encoding="utf-8")

    assert not process_file(str(f), fix_mode=True)


def test_process_file_updates_incorrect_header(tmp_path: Path) -> None:
    """Verifies that incorrect headers (e.g. wrong path) are updated."""
    f = tmp_path / "wrong.py"
    f.write_text("# File: wrong/path.py\nprint('hi')\n", encoding="utf-8")

    assert process_file(str(f), fix_mode=True)

    content = f.read_text(encoding="utf-8")
    assert content.startswith(f"# File: {f.as_posix()}\n")


def test_process_file_clamps_index(tmp_path: Path) -> None:
    """Verifies that out-of-bounds insertion indices are clamped to file length."""
    f = tmp_path / "clamp.py"
    f.write_text("print('hi')\n", encoding="utf-8")

    # Mock strategy to return huge index
    with patch("context_headers.core.get_strategy_for_file") as mock_factory:
        mock_strategy = MagicMock()
        mock_factory.return_value = mock_strategy
        mock_strategy.get_expected_header.return_value = "# File: ...\n"
        mock_strategy.get_insertion_index.return_value = 100
        mock_strategy.is_header_line.return_value = False

        assert process_file(str(f), fix_mode=True)

        lines = f.read_text(encoding="utf-8").splitlines()
        # Should append at end (index 1, len was 1)
        assert lines[-1] == "# File: ...\n".strip()


def test_process_file_skips_unsafe_strategy_return(tmp_path: Path) -> None:
    """Verifies that process_file returns False when strategy returns -1.

    This ensures that ambiguous files (like PHP files containing only HTML)
    are skipped to prevent data corruption, covering the safety check in core.py.
    """
    f = tmp_path / "ambiguous.php"
    # PhpStrategy returns -1 if no <?php tag is found
    f.write_text("<html>No PHP tag here</html>", encoding="utf-8")

    # Should return False (no change made)
    assert not process_file(str(f), fix_mode=True)

    # File should be unchanged
    assert f.read_text(encoding="utf-8") == "<html>No PHP tag here</html>"


def test_process_file_skips_mandatory_exclusions(tmp_path: Path) -> None:
    """Verifies that lockfiles (e.g., Cargo.lock) are skipped even if extension matches."""
    # Cargo.lock is TOML, but we don't want to touch it.
    f = tmp_path / "Cargo.lock"
    f.write_text('[package]\nname = "foo"\n', encoding="utf-8")

    assert not process_file(str(f), fix_mode=True)

    # Content should remain untouched
    assert f.read_text(encoding="utf-8") == '[package]\nname = "foo"\n'


def test_process_file_skips_uv_lock(tmp_path: Path) -> None:
    """Verifies that uv.lock is skipped as a mandatory exclusion."""
    f = tmp_path / "uv.lock"
    f.write_text("version = 1\n", encoding="utf-8")
    assert not process_file(str(f), fix_mode=True)
    assert f.read_text(encoding="utf-8") == "version = 1\n"


def test_process_file_remove_mode_success(tmp_path: Path) -> None:
    """Verifies that remove_mode=True successfully removes an existing header."""
    f = tmp_path / "remove.py"
    # Create file with a header
    f.write_text("# File: some/path.py\nprint('hello')\n", encoding="utf-8")

    assert process_file(str(f), fix_mode=False, remove_mode=True)

    # Header should be gone
    assert f.read_text(encoding="utf-8") == "print('hello')\n"


def test_process_file_remove_mode_no_header(tmp_path: Path) -> None:
    """Verifies that remove_mode=True does nothing if no header exists."""
    f = tmp_path / "clean.py"
    f.write_text("print('hello')\n", encoding="utf-8")

    assert not process_file(str(f), fix_mode=False, remove_mode=True)
    assert f.read_text(encoding="utf-8") == "print('hello')\n"
