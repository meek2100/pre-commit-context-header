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


def test_process_file_write_error(tmp_path: Path) -> None:
    """Verifies that OSErrors during file writing are handled gracefully."""
    f = tmp_path / "write_error.py"
    f.write_text("print('hi')\n", encoding="utf-8")

    # Mock write_text to raise PermissionError
    with patch(
        "pathlib.Path.write_text", side_effect=PermissionError("Permission denied")
    ):
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

    # For removal to actually happen in core API, fix_mode must be True
    assert process_file(str(f), fix_mode=True, remove_mode=True)

    # Header should be gone
    assert f.read_text(encoding="utf-8") == "print('hello')\n"


def test_process_file_remove_mode_no_header(tmp_path: Path) -> None:
    """Verifies that remove_mode=True does nothing if no header exists."""
    f = tmp_path / "clean.py"
    f.write_text("print('hello')\n", encoding="utf-8")

    assert not process_file(str(f), fix_mode=False, remove_mode=True)
    assert f.read_text(encoding="utf-8") == "print('hello')\n"


def test_process_file_with_whitespace_before_header(tmp_path: Path) -> None:
    """Verifies idempotency when whitespace is added before an existing header."""
    f = tmp_path / "whitespace.md"
    f.write_text("---\ntitle: test\n---\n# Body\n", encoding="utf-8")

    # 1. First run adds header
    process_file(str(f), fix_mode=True)
    first_pass = f.read_text()
    assert "<!-- File:" in first_pass

    # 2. Simulate formatter adding a newline before header
    lines = first_pass.splitlines(keepends=True)
    # Header is at index 3 in a file with 3 frontmatter lines
    lines.insert(3, "\n")
    f.write_text("".join(lines), encoding="utf-8")

    # 3. Second run should NOT add a new header (idempotent)
    assert not process_file(str(f), fix_mode=True)
    assert f.read_text().count("<!-- File:") == 1


def test_remove_mode_skips_whitespace(tmp_path: Path) -> None:
    """Verifies that remove_mode skips whitespace to find and remove the header."""
    f = tmp_path / "remove_ws.md"
    # Header separated by two newlines
    f.write_text(
        "---\ntitle: test\n---\n\n\n<!-- File: remove_ws.md -->\n# Body\n",
        encoding="utf-8",
    )

    # For removal to actually happen in core API, fix_mode must be True
    assert process_file(str(f), fix_mode=True, remove_mode=True)

    content = f.read_text()
    assert "<!-- File:" not in content
    assert "# Body" in content


def test_process_file_deduplication(tmp_path: Path) -> None:
    """Verifies that multiple headers are deduplicated to a single correct one."""
    f = tmp_path / "dedup.py"
    # 1. Correct header at index 2, but misplaced headers at 0 and 3 (all in preamble)
    correct_header = f"# File: {f.as_posix()}\n"
    content = (
        "# File: wrong.py\n"  # Misplaced 1
        "#!/usr/bin/env python\n"
        "# File: extra.py\n"  # Misplaced 2 (Duplicate)
        "\n"  # Empty line (Still preamble)
        "print('hi')\n"  # FIRST CODE LINE
        "# Case: This header should BE PROTECTED because it is after code\n"
        "# File: protected.py\n"
    )
    f.write_text(content, encoding="utf-8")

    # Run in fix mode
    assert process_file(str(f), fix_mode=True)

    final_content = f.read_text()
    # We expect count to be 2: One correct at the top, one protected in the body
    assert final_content.count("# File:") == 2
    assert final_content.startswith(f"#!/usr/bin/env python\n{correct_header}")
    assert "# File: protected.py" in final_content


def test_process_file_dedup_on_addition(tmp_path: Path) -> None:
    """Verifies reporting when adding a header AND removing duplicates (hits line 167)."""
    f = tmp_path / "add_dedup.py"
    # File with no header at ideal spot, but a duplicate elsewhere
    content = "#!/usr/bin/env python\n# File: extra.py\nprint('hi')\n"
    f.write_text(content, encoding="utf-8")
    assert process_file(str(f), fix_mode=True)
    assert f.read_text().count("# File:") == 1


def test_process_file_no_fix_dedup_only(tmp_path: Path) -> None:
    """Verifies reporting when only duplicates exist in check mode (hits line 139)."""
    f = tmp_path / "check_dedup.py"
    correct_header = f"# File: {f.as_posix()}\n"
    f.write_text(f"{correct_header}{correct_header}print('hi')\n", encoding="utf-8")
    assert process_file(str(f), fix_mode=False)


def test_process_file_remove_mode_dry_run(tmp_path: Path) -> None:
    """Verifies dry-run remove reporting (hits line 117)."""
    f = tmp_path / "remove_dry.py"
    f.write_text("# File: test.py\nprint('hi')\n", encoding="utf-8")
    assert process_file(str(f), fix_mode=False, remove_mode=True)


def test_declaration_strategy_multiline_discovery(tmp_path: Path) -> None:
    """Verifies multiline discovery in DeclarationStrategy (hits lines 166, 174)."""
    # 1. Multiline XML
    xml = tmp_path / "multi.xml"
    xml.write_text("<?xml\nversion='1.0'?>\n<root/>\n", encoding="utf-8")
    assert process_file(str(xml), fix_mode=True)
    assert xml.read_text().startswith("<?xml\nversion='1.0'?>\n<!-- File:")

    # 2. Multiline CSS
    css = tmp_path / "multi.css"
    css.write_text("@charset\n'UTF-8';\nbody {}\n", encoding="utf-8")
    assert process_file(str(css), fix_mode=True)
    assert css.read_text().startswith("@charset\n'UTF-8';\n/* File:")


def test_php_strategy_extra_skips(tmp_path: Path) -> None:
    """Verifies PHP strategy safety skips for XML and one-liners (hits line 204)."""
    # One-liner PHP should be skipped
    php = tmp_path / "oneliner.php"
    php.write_text("<?php echo 'hi'; ?>\n", encoding="utf-8")
    assert not process_file(str(php), fix_mode=True)


def test_process_file_remove_mode_deduplicates(tmp_path: Path) -> None:
    """Verifies that remove_mode removes ALL headers from a file."""
    f = tmp_path / "remove_all.py"
    f.write_text("# File: 1.py\n# File: 2.py\nprint('hi')\n", encoding="utf-8")

    assert process_file(str(f), fix_mode=True, remove_mode=True)
    assert f.read_text() == "print('hi')\n"


def test_process_file_no_fix_dedup_report(tmp_path: Path) -> None:
    """Verifies that deduplication is reported in check-only mode."""
    f = tmp_path / "dedup_report.py"
    f.write_text("# File: 1.py\n# File: 1.py\nprint('hi')\n", encoding="utf-8")

    # Correct header but duplicate
    assert process_file(str(f), fix_mode=False)


def test_process_file_incorrect_and_dedup_report(tmp_path: Path) -> None:
    """Verifies that incorrect + duplicate is reported in check-only mode."""
    f = tmp_path / "wrong_dedup.py"
    f.write_text("# File: wrong.py\n# File: extra.py\nprint('hi')\n", encoding="utf-8")

    assert process_file(str(f), fix_mode=False)


def test_strategies_with_headers_discovery(tmp_path: Path) -> None:
    """Verifies that all strategies can find directives underneath existing headers."""
    # 1. Dockerfile
    df = tmp_path / "Dockerfile"
    df.write_text(
        "# File: test.dockerfile\n# syntax=docker/dockerfile:1\nFROM alpine\n",
        encoding="utf-8",
    )
    # Should move header after directive
    assert process_file(str(df), fix_mode=True)
    assert df.read_text().startswith("# syntax=docker/dockerfile:1\n# File:")

    # 2. Python
    py = tmp_path / "discovery.py"
    py.write_text(
        "# File: old.py\n# -*- coding: utf-8 -*-\nprint('hi')\n", encoding="utf-8"
    )
    assert process_file(str(py), fix_mode=True)
    assert py.read_text().startswith("# -*- coding: utf-8 -*-\n# File:")

    # 3. PHP
    php = tmp_path / "discovery.php"
    php.write_text("// File: old.php\n<?php\necho 'hi';\n", encoding="utf-8")
    assert process_file(str(php), fix_mode=True)
    assert php.read_text().startswith("<?php\n// File:")

    # 4. Frontmatter
    md = tmp_path / "discovery.md"
    md.write_text(
        "<!-- File: old.md -->\n---\ntitle: test\n---\nbody\n", encoding="utf-8"
    )
    assert process_file(str(md), fix_mode=True)
    assert "---\ntitle: test\n---\n<!-- File:" in md.read_text()


def test_python_strategy_cookie_only_with_header(tmp_path: Path) -> None:
    """Verifies PythonStrategy with header then cookie (no shebang)."""
    py = tmp_path / "cookie_only.py"
    py.write_text("# File: old.py\n# -*- coding: utf-8 -*-\n", encoding="utf-8")
    assert process_file(str(py), fix_mode=True)
    # Selection logic:
    # idx=1 (skips header). base_idx=1.
    # scan for cookie starting at 1. Finds it at 1. returns 2.
    # core.py removes 0, adds at 2.
    assert py.read_text().startswith("# -*- coding: utf-8 -*-\n# File:")


def test_dockerfile_strategy_no_discovery(tmp_path: Path) -> None:
    """Verifies DockerfileStrategy when only headers exist (should return 0)."""
    df = tmp_path / "Dockerfile.no_disc"
    header = f"# File: {df.as_posix()}\n"
    df.write_text(f"{header}FROM alpine\n", encoding="utf-8")
    assert not process_file(str(df), fix_mode=True)


def test_strategy_edge_cases(tmp_path: Path) -> None:
    """Verifies safety skips and edge cases for strategies to reach 100% coverage."""
    # 1. Shebang empty file
    empty = tmp_path / "empty.sh"
    empty.touch()
    assert process_file(str(empty), fix_mode=True)

    # 2. Dockerfile with Shebang discovered
    df = tmp_path / "Dockerfile.shebang"
    df.write_text("#!/bin/sh\nFROM alpine\n", encoding="utf-8")
    assert process_file(str(df), fix_mode=True)
    assert df.read_text().startswith("#!/bin/sh\n# File:")

    # 3. Declaration multiline skip (fail to find end)
    xml = tmp_path / "unsafe.xml"
    # Create multiple lines so it enters the loop but fails to find '>'
    xml.write_text("<?xml version='1.0'\nline 2\nline 3\n", encoding="utf-8")
    assert not process_file(str(xml), fix_mode=True)

    # 4. PHP XML skip (unsafe to insert before XML decl in PHP)
    php = tmp_path / "unsafe.php"
    php.write_text("<?xml version='1.0' encoding='UTF-8'?>\n<?php\n", encoding="utf-8")
    assert not process_file(str(php), fix_mode=True)

    # 5. Frontmatter unclosed skip
    md = tmp_path / "unsafe.md"
    md.write_text("---\ntitle: unclosed\nbody\n", encoding="utf-8")
    assert not process_file(str(md), fix_mode=True)

    # 6. File only headers (DeclarationStrategy)
    only_h = tmp_path / "only.xml"
    only_h.write_text("<!-- File: 1.xml -->\n<!-- File: 2.xml -->\n", encoding="utf-8")
    assert process_file(str(only_h), fix_mode=True)  # Deduplicates to one

    # 7. Unclosed CSS
    css = tmp_path / "unsafe.css"
    css.write_text("@charset 'UTF-8'\nbody {}\n", encoding="utf-8")  # No semicolon
    assert not process_file(str(css), fix_mode=True)
