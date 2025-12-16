# File: tests/test_context_header.py
import pytest
from pathlib import Path
from context_headers import process_file, get_insertion_index


def test_insertion_index_simple():
    lines = ["print('hello')\n"]
    assert get_insertion_index(lines) == 0


def test_insertion_index_shebang():
    lines = ["#!/usr/bin/env python3\n", "print('hello')\n"]
    assert get_insertion_index(lines) == 1


def test_insertion_index_encoding():
    lines = ["# -*- coding: utf-8 -*-\n", "print('hello')\n"]
    assert get_insertion_index(lines) == 1


def test_insertion_index_shebang_and_encoding():
    lines = [
        "#!/usr/bin/env python3\n",
        "# -*- coding: utf-8 -*-\n",
        "print('hello')\n",
    ]
    assert get_insertion_index(lines) == 2


def test_process_file_adds_header(tmp_path):
    f = tmp_path / "test.py"
    f.write_text("print('hello')\n", encoding="utf-8")

    # Run in fix mode
    assert process_file(str(f), fix_mode=True)

    content = f.read_text(encoding="utf-8")
    expected = f"# File: {f.as_posix()}\nprint('hello')\n"
    assert content == expected


def test_process_file_is_idempotent(tmp_path):
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


def test_process_file_skips_binary(tmp_path):
    f = tmp_path / "test.exe"
    f.write_bytes(b"\x00\x01\x02")  # Not utf-8
    assert not process_file(str(f), fix_mode=True)


def test_process_file_skips_empty(tmp_path):
    f = tmp_path / "empty.py"
    f.touch()
    assert not process_file(str(f), fix_mode=True)
    assert f.read_text() == ""


def test_html_comment_style(tmp_path):
    f = tmp_path / "index.html"
    f.write_text("<div>Content</div>", encoding="utf-8")

    process_file(str(f), fix_mode=True)

    content = f.read_text(encoding="utf-8")
    # Verify we are adding a visible HTML comment, not just a newline
    assert content.startswith("
