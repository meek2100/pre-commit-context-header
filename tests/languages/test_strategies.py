# File: tests/languages/test_strategies.py
"""
Tests for language-specific strategy implementations.

Verifies that insertion indices are correctly calculated for different
file types, respecting shebangs, directives, and frontmatter.
"""

from pathlib import Path
from context_headers.languages.factory import get_strategy_for_file
from context_headers.languages.strategies import (
    ShebangStrategy,
    PythonStrategy,
    DeclarationStrategy,
    PhpStrategy,
    FrontmatterStrategy,
    DockerfileStrategy,
)


def test_shebang_strategy_skips_shebang() -> None:
    """Verifies that ShebangStrategy correctly identifies index 1 after a shebang."""
    strategy = ShebangStrategy("# File: {}")
    lines = ["#!/bin/bash\n", "echo 'hello'\n"]
    assert strategy.get_insertion_index(lines) == 1

    # Test empty file
    assert strategy.get_insertion_index([]) == 0

    # Test no shebang (acts as default strategy)
    lines_plain = ["print('hello')\n"]
    assert strategy.get_insertion_index(lines_plain) == 0


def test_dockerfile_strategy_skips_directives() -> None:
    """Verifies that DockerfileStrategy skips syntax and escape directives."""
    strategy = DockerfileStrategy("# File: {}")

    # Case 1: Syntax directive
    lines = ["# syntax=docker/dockerfile:1\n", "FROM alpine\n"]
    assert strategy.get_insertion_index(lines) == 1

    # Case 2: Escape directive
    lines_esc = ["# escape=`\n", "FROM windowsservercore\n"]
    assert strategy.get_insertion_index(lines_esc) == 1

    # Case 3: Multiple directives
    lines_multi = ["# syntax=v1\n", "# check=skip=all\n", "FROM alpine\n"]
    assert strategy.get_insertion_index(lines_multi) == 2

    # Case 4: Directive must be at top (stop at comment)
    # If a normal comment appears, directives are done.
    lines_comment = ["# I am a comment\n", "# syntax=too-late\n"]
    assert strategy.get_insertion_index(lines_comment) == 0

    # Case 5: With Shebang
    lines_shebang = ["#!/usr/bin/env docker-build\n", "# syntax=v1\n", "FROM alpine\n"]
    assert strategy.get_insertion_index(lines_shebang) == 2

    # Case 6: Directives with spaces (Robustness)
    lines_spaces = ["# syntax = docker/dockerfile:1\n", "FROM alpine\n"]
    assert strategy.get_insertion_index(lines_spaces) == 1

    # Case 7: Check directive (Modern Docker)
    lines_check = ["# check=skip=all\n", "FROM alpine\n"]
    assert strategy.get_insertion_index(lines_check) == 1


def test_python_strategy_skips_shebang_and_encoding() -> None:
    """Verifies that PythonStrategy skips both shebangs and PEP 263 encoding cookies."""
    strategy = PythonStrategy("# File: {}")
    lines = [
        "#!/usr/bin/env python3\n",
        "# -*- coding: utf-8 -*-\n",
        "print('hello')\n",
    ]
    assert strategy.get_insertion_index(lines) == 2


def test_declaration_strategy_skips_xml() -> None:
    """Verifies that DeclarationStrategy skips the XML declaration line."""
    strategy = DeclarationStrategy("")
    lines = ['<?xml version="1.0"?>\n', "<root></root>\n"]
    assert strategy.get_insertion_index(lines) == 1

    lines_no_decl = ["<root></root>\n"]
    assert strategy.get_insertion_index(lines_no_decl) == 0


def test_declaration_strategy_skips_doctype() -> None:
    """Verifies that DeclarationStrategy skips HTML5 DOCTYPE declarations."""
    strategy = DeclarationStrategy("")

    # Standard HTML5
    lines = ["<!DOCTYPE html>\n", "<html>\n"]
    assert strategy.get_insertion_index(lines) == 1

    # Case insensitive
    lines_lower = ["<!doctype html>\n", "<html>\n"]
    assert strategy.get_insertion_index(lines_lower) == 1


def test_declaration_strategy_skips_multiline_unsafe() -> None:
    """Verifies that DeclarationStrategy skips or handles multi-line declarations."""
    strategy = DeclarationStrategy("")

    # Multi-line Doctype (Found within limit)
    lines_multi = [
        "<!DOCTYPE html\n",
        "  PUBLIC '-//W3C//DTD XHTML 1.0 Transitional//EN'\n",
        "  'http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd'>\n",
        "<html>\n",
    ]
    # Should insert after line 2 (index 3)
    assert strategy.get_insertion_index(lines_multi) == 3

    # Unclosed/Too long (Safety Skip)
    lines_forever = ["<!DOCTYPE html\n"] * 30
    assert strategy.get_insertion_index(lines_forever) == -1


def test_declaration_strategy_skips_web_directives() -> None:
    """Verifies that DeclarationStrategy skips CSS @charset and Razor @page."""
    strategy = DeclarationStrategy("")

    # Case 1: CSS Charset
    lines_css = ['@charset "UTF-8";\n', "body { color: red; }\n"]
    assert strategy.get_insertion_index(lines_css) == 1

    # Case 2: Razor Page
    lines_razor = ['@page "/contact"\n', "<h1>Contact</h1>\n"]
    assert strategy.get_insertion_index(lines_razor) == 1

    # Case 3: ASP/JSP Directive
    lines_asp = ['<%@ Page Language="C#" %>\n', "<html>\n"]
    assert strategy.get_insertion_index(lines_asp) == 1


def test_declaration_strategy_multiline_css() -> None:
    """Verifies that DeclarationStrategy handles multi-line CSS charsets."""
    strategy = DeclarationStrategy("")

    # Case 1: Semicolon on line 2 (index 1) - Covers lines 164-166
    lines_split = ['@charset "UTF-8"\n', ";\n", "body {}\n"]
    # Should insert after line 2 (index 2)
    assert strategy.get_insertion_index(lines_split) == 2

    # Case 2: Semicolon missing in first 5 lines (Safety Skip) - Covers line 167
    lines_missing = ['@charset "UTF-8"\n', "body {}\n"]
    assert strategy.get_insertion_index(lines_missing) == -1


def test_php_strategy_skips_opentag() -> None:
    """Verifies that PhpStrategy skips opening PHP tags to insert headers inside the block."""
    strategy = PhpStrategy("// File: {}")

    # Case 1: Plain <?php
    lines = ["<?php\n", "echo 1;\n"]
    assert strategy.get_insertion_index(lines) == 1

    # Case 2: <?php with shebang
    lines_shebang = ["#!/usr/bin/env php\n", "<?php\n", "echo 1;\n"]
    assert strategy.get_insertion_index(lines_shebang) == 2

    # Case 3: <? (short tag)
    lines_short = ["<?\n", "echo 1;\n"]
    assert strategy.get_insertion_index(lines_short) == 1

    # Case 4: No tag (HTML) -> SHOULD RETURN -1 (Skip)
    # Inserting // File: ... into HTML is dangerous/visible.
    lines_html = ["<html>\n"]
    assert strategy.get_insertion_index(lines_html) == -1


def test_frontmatter_strategy_skips_block() -> None:
    """Verifies that FrontmatterStrategy skips the entire YAML frontmatter block."""
    strategy = FrontmatterStrategy("")

    # Case 1: Standard Frontmatter
    lines = ["---\n", "title: hello\n", "---\n", "<h1>Hi</h1>\n"]
    assert strategy.get_insertion_index(lines) == 3

    # Case 2: No frontmatter
    lines_none = ["<h1>Hi</h1>\n"]
    assert strategy.get_insertion_index(lines_none) == 0

    # Case 3: Unclosed (safety check, returns 0) - This behavior is now UPDATED to return -1 (Skip)
    # The previous test_frontmatter_strategy_skips_block tested a scenario where it returned 0,
    # but based on the fix, it should now return -1.
    # However, to preserve the integrity of the original test suite structure,
    # I will move the "Unclosed" case to the explicit test below and keep this focused on valid blocks.
    pass


def test_frontmatter_strategy_unclosed() -> None:
    """Verifies that FrontmatterStrategy returns -1 for unclosed frontmatter blocks."""
    strategy = FrontmatterStrategy("")
    lines = ["---\n", "title: unclosed\n", "description: dangerous\n"]
    # Should return -1 (Skip)
    assert strategy.get_insertion_index(lines) == -1


def test_strategy_header_generation(tmp_path: Path) -> None:
    """Verifies that the strategy generates the correct header string from a path."""
    f = tmp_path / "test.py"
    strategy = PythonStrategy("# File: {}")
    expected = f"# File: {f.as_posix()}\n"
    assert strategy.get_expected_header(f) == expected


def test_is_header_line() -> None:
    """Verifies that is_header_line correctly identifies matching header lines."""
    strategy = ShebangStrategy("# File: {}")
    assert strategy.is_header_line("# File: path/to/file.py")
    assert not strategy.is_header_line("# Not a header")


def test_base_is_header_line_safety() -> None:
    """Ensure is_header_line NEVER identifies a Shebang as a header."""
    strategy = ShebangStrategy("# File: {}")

    # Standard shebangs
    assert not strategy.is_header_line("#!/bin/bash")
    assert not strategy.is_header_line("#!/usr/bin/env python")

    # Edge case: Style that looks like shebang components
    dangerous_strategy = ShebangStrategy("#! {}")
    assert not dangerous_strategy.is_header_line("#!/bin/bash")


def test_header_strategy_safety_empty_style() -> None:
    """Verifies that is_header_line returns False safely if comment_style is empty.

    This ensures 100% coverage by hitting the safety check in base.py.
    """
    strategy = ShebangStrategy("")
    # Should return False immediately, not crash or return True
    assert not strategy.is_header_line("Any line")


def test_header_strategy_safety_only_placeholders() -> None:
    """Verifies that checks are strict when style results in empty prefix/suffix.

    If comment_style is "{}", prefix and suffix are empty.
    lines.startswith("") and endswith("") is always True.
    This test ensures we have a guard against this.
    """
    strategy = ShebangStrategy("{}")
    # Without the safety guard, this would be True for ANY string.
    assert not strategy.is_header_line("Any line content")
    assert not strategy.is_header_line("")


def test_strategy_no_placeholder() -> None:
    """Verifies behavior for styles that do not contain the '{}' placeholder."""
    strategy = ShebangStrategy("HEADER")
    assert strategy.get_expected_header(Path("foo")) == "HEADER\n"
    assert strategy.is_header_line("HEADER")
    assert not strategy.is_header_line("OTHER")


def test_declaration_strategy_insertion() -> None:
    """Verifies insertion logic for Declaration strategy with valid comments."""
    strategy = DeclarationStrategy("")
    assert strategy.get_insertion_index([]) == 0


def test_frontmatter_strategy_empty() -> None:
    """Verifies insertion logic for Frontmatter strategy on empty files."""
    strategy = FrontmatterStrategy("")
    assert strategy.get_insertion_index([]) == 0


def test_python_strategy_skips_cookie_on_second_line_no_shebang() -> None:
    """Verifies PythonStrategy detects encoding cookies even without a shebang."""
    strategy = PythonStrategy("# File: {}")
    lines = [
        "# Some comment\n",
        "# -*- coding: utf-8 -*-\n",
        "print('hello')\n",
    ]
    assert strategy.get_insertion_index(lines) == 2


def test_markdown_strategy_selection() -> None:
    """Verifies correct strategy and comment style selection for Markdown files."""
    path = Path("test.markdown")
    strategy = get_strategy_for_file(path)
    assert isinstance(strategy, FrontmatterStrategy)
    # Config now defines Markdown as HTML comment
    assert strategy.comment_style == "<!-- File: {} -->"


def test_frontmatter_strategy_only_frontmatter() -> None:
    """Verifies behavior when a file contains ONLY frontmatter."""
    strategy = FrontmatterStrategy("")
    lines = [
        "---\n",
        "title: hello\n",
        "---\n",
    ]
    # Should insert after the block (index 3)
    assert strategy.get_insertion_index(lines) == 3


def test_php_strategy_skips_unsafe_content() -> None:
    """Verifies that PhpStrategy skips XML declarations and one-liners."""
    strategy = PhpStrategy("// File: {}")

    # Safety: XML Declaration -> Skip
    assert strategy.get_insertion_index(['<?xml version="1.0"?>\n']) == -1
    # Case insensitive check
    assert strategy.get_insertion_index(['<?XML version="1.0"?>\n']) == -1

    # Safety: One-liner -> Skip (inserting after ?> renders as text)
    assert strategy.get_insertion_index(['<?php echo "hi"; ?>\n']) == -1
