# File: tests/test_context_header.py
import pytest
from pathlib import Path
from context_headers import process_file, get_insertion_index, MAX_FILE_SIZE_BYTES, is_header_line, main
from unittest.mock import patch
import sys

def test_insertion_index_simple() -> None:
    lines = ["print('hello')\n"]
    assert get_insertion_index(lines) == 0


def test_insertion_index_shebang() -> None:
    lines = ["#!/usr/bin/env python3\n", "print('hello')\n"]
    assert get_insertion_index(lines) == 1


def test_insertion_index_encoding() -> None:
    lines = ["# -*- coding: utf-8 -*-\n", "print('hello')\n"]
    assert get_insertion_index(lines) == 1


def test_insertion_index_shebang_and_encoding() -> None:
    lines = [
        "#!/usr/bin/env python3\n",
        "# -*- coding: utf-8 -*-\n",
        "print('hello')\n",
    ]
    assert get_insertion_index(lines) == 2


def test_process_file_adds_header(tmp_path: Path) -> None:
    f = tmp_path / "test.py"
    f.write_text("print('hello')\n", encoding="utf-8")

    # Run in fix mode
    assert process_file(str(f), fix_mode=True)

    content = f.read_text(encoding="utf-8")
    expected = f"# File: {f.as_posix()}\nprint('hello')\n"
    assert content == expected


def test_process_file_is_idempotent(tmp_path: Path) -> None:
    """Ensure running the tool twice doesn't duplicate headers."""
    f = tmp_path / "repeat.py"
    f.write_text("print('once')\n", encoding="utf-8")

    # First run: Adds header
    assert process_file(str(f), fix_mode=True)
    content_first_pass = f.read_text(encoding="utf-8")

    # Second run: Should return False (no changes needed)
    assert not process_file(str(f), fix_mode=True)

    # Content should remain exactly the same
    assert f.read_text(encoding="utf-8") == content_first_pass


def test_process_file_skips_binary(tmp_path: Path) -> None:
    f = tmp_path / "test.exe"
    f.write_bytes(b"\x00\x01\x02")  # Not utf-8
    assert not process_file(str(f), fix_mode=True)


def test_process_file_skips_empty(tmp_path: Path) -> None:
    f = tmp_path / "empty.py"
    f.touch()
    assert not process_file(str(f), fix_mode=True)
    assert f.read_text() == ""


def test_html_comment_style(tmp_path: Path) -> None:
    f = tmp_path / "index.html"
    f.write_text("<div>Content</div>", encoding="utf-8")

    process_file(str(f), fix_mode=True)

    content = f.read_text(encoding="utf-8")
    # Verify we are adding a visible HTML comment
    # Note: process_file ensures the file ends with a newline, so we expect one here.
    expected = f"<!-- File: {f.as_posix()} -->\n<div>Content</div>\n"
    assert content == expected

def test_xml_comment_style(tmp_path: Path) -> None:
    f = tmp_path / "config.xml"
    f.write_text("<root></root>", encoding="utf-8")

    process_file(str(f), fix_mode=True)

    content = f.read_text(encoding="utf-8")
    expected = f"<!-- File: {f.as_posix()} -->\n<root></root>\n"
    assert content == expected

def test_vue_comment_style(tmp_path: Path) -> None:
    f = tmp_path / "App.vue"
    f.write_text("<template></template>", encoding="utf-8")

    process_file(str(f), fix_mode=True)

    content = f.read_text(encoding="utf-8")
    expected = f"<!-- File: {f.as_posix()} -->\n<template></template>\n"
    assert content == expected

def test_md_comment_style(tmp_path: Path) -> None:
    f = tmp_path / "README.md"
    f.write_text("# Title", encoding="utf-8")

    process_file(str(f), fix_mode=True)

    content = f.read_text(encoding="utf-8")
    expected = f"<!-- File: {f.as_posix()} -->\n# Title\n"
    assert content == expected

def test_process_file_large_file(tmp_path: Path) -> None:
    f = tmp_path / "large.py"
    f.write_text("print('large')", encoding="utf-8")

    # Mock stat to return size > MAX_FILE_SIZE_BYTES
    with patch("pathlib.Path.stat") as mock_stat:
        mock_stat.return_value.st_size = MAX_FILE_SIZE_BYTES + 1
        assert not process_file(str(f), fix_mode=True)

    # Verify content is unchanged
    assert f.read_text(encoding="utf-8") == "print('large')"

def test_process_file_permission_error(tmp_path: Path) -> None:
    f = tmp_path / "protected.py"
    f.write_text("print('secret')", encoding="utf-8")

    # Mock stat to raise PermissionError
    with patch("pathlib.Path.stat", side_effect=PermissionError("Permission denied")):
        assert not process_file(str(f), fix_mode=True)

def test_process_file_update_incorrect_header(tmp_path: Path) -> None:
    f = tmp_path / "wrong.py"
    # Write a file with an incorrect header (e.g. from a rename or just wrong content)

    # Manually write a header that looks like a header but has wrong path
    f.write_text("# File: old/path/wrong.py\nprint('hello')\n", encoding="utf-8")

    assert process_file(str(f), fix_mode=True)

    content = f.read_text(encoding="utf-8")
    expected = f"# File: {f.as_posix()}\nprint('hello')\n"
    assert content == expected

def test_process_file_no_fix_mode(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    f = tmp_path / "nofix.py"
    f.write_text("print('hello')\n", encoding="utf-8")

    # Run in check mode (fix_mode=False)
    assert process_file(str(f), fix_mode=False)

    # Content should remain unchanged
    assert f.read_text(encoding="utf-8") == "print('hello')\n"

    # Check output
    captured = capsys.readouterr()
    assert "Missing or incorrect header" in captured.out

def test_dockerfile(tmp_path: Path) -> None:
    f = tmp_path / "Dockerfile"
    f.write_text("FROM python:3\n", encoding="utf-8")

    assert process_file(str(f), fix_mode=True)

    content = f.read_text(encoding="utf-8")
    expected = f"# File: {f.as_posix()}\nFROM python:3\n"
    assert content == expected

def test_unknown_extension(tmp_path: Path) -> None:
    f = tmp_path / "unknown.xyz"
    f.write_text("content", encoding="utf-8")

    assert not process_file(str(f), fix_mode=True)
    assert f.read_text(encoding="utf-8") == "content"

def test_process_file_read_oserror(tmp_path: Path) -> None:
    f = tmp_path / "unreadable.py"
    f.write_text("content", encoding="utf-8")

    # Mock read_text to raise OSError
    with patch("pathlib.Path.read_text", side_effect=OSError("Read error")):
        assert not process_file(str(f), fix_mode=True)

def test_process_file_missing_newline_at_eof(tmp_path: Path) -> None:
    f = tmp_path / "no_newline.py"
    f.write_text("print('hello')", encoding="utf-8") # No newline at end

    process_file(str(f), fix_mode=True)

    content = f.read_text(encoding="utf-8")
    # Should add header AND ensure newline at end of original last line (which is now after header)
    expected = f"# File: {f.as_posix()}\nprint('hello')\n"
    assert content == expected

def test_is_header_line_edge_cases() -> None:
    # Test unknown extension
    assert not is_header_line("# File: foo", ".unknown")
    # Test style without format string (unlikely but possible logic)
    # We can fake the style in COMMENT_STYLES if we patch it
    with patch.dict("context_headers.COMMENT_STYLES", {".test": "PREFIX"}):
        assert is_header_line("PREFIX", ".test")
        assert not is_header_line("OTHER", ".test")

def test_insertion_index_empty_lines() -> None:
    assert get_insertion_index([]) == 0

def test_insertion_index_shebang_only_greater_than_len(tmp_path: Path) -> None:
    # This line: if insert_idx > len(lines): insert_idx = len(lines)
    # is only reachable if get_insertion_index returns something > len(lines).

    f = tmp_path / "index_test.py"
    f.write_text("print('hi')\n", encoding="utf-8")

    with patch("context_headers.get_insertion_index", return_value=100):
        # This will trigger the clamping logic
        process_file(str(f), fix_mode=True)
        # Verify it appended at the end
        content = f.read_text(encoding="utf-8")
        assert content.endswith("# File: " + f.as_posix() + "\n")

def test_main_cli_fix(tmp_path: Path) -> None:
    f = tmp_path / "cli_test.py"
    f.write_text("print('cli')\n", encoding="utf-8")

    with patch("sys.argv", ["context-headers", "--fix", str(f)]), pytest.raises(SystemExit) as e:
        main()
    assert e.value.code == 1
    assert f.read_text().startswith("# File:")

def test_main_cli_check_fail(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    f = tmp_path / "cli_fail.py"
    f.write_text("print('fail')\n", encoding="utf-8")

    with patch("sys.argv", ["context-headers", str(f)]), pytest.raises(SystemExit) as e:
        main()
    assert e.value.code == 1
    captured = capsys.readouterr()
    assert "missing/incorrect headers" in captured.out

def test_main_cli_check_pass(tmp_path: Path) -> None:
    f = tmp_path / "cli_pass.py"
    f.write_text(f"# File: {f.as_posix()}\nprint('pass')\n", encoding="utf-8")

    with patch("sys.argv", ["context-headers", str(f)]), pytest.raises(SystemExit) as e:
        main()
    assert e.value.code == 0

def test_main_cli_no_args() -> None:
    with patch("sys.argv", ["context-headers"]), pytest.raises(SystemExit) as e:
        main()
    assert e.value.code == 0

def test_run_as_script(tmp_path: Path) -> None:
    # This will actually run the file as a script using subprocess, verifying the `if __name__ == "__main__":` block.
    import subprocess

    cmd = [sys.executable, "context_headers.py", "--help"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    assert result.returncode == 0
    assert "Enforce file path headers" in result.stdout
