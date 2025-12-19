# File: tests/languages/test_strategies.py
from pathlib import Path
from context_headers.languages.factory import get_strategy_for_file
from context_headers.languages.strategies import (
    DefaultStrategy,
    ShebangStrategy,
    PythonStrategy,
    XmlStrategy,
    PhpStrategy,
    FrontmatterStrategy,
)


def test_default_strategy_insertion() -> None:
    strategy = DefaultStrategy("/* File: {} */")
    lines = ["body { color: red; }\n"]
    assert strategy.get_insertion_index(lines) == 0


def test_shebang_strategy_skips_shebang() -> None:
    strategy = ShebangStrategy("# File: {}")
    lines = ["#!/bin/bash\n", "echo 'hello'\n"]
    assert strategy.get_insertion_index(lines) == 1

    # Test empty file
    assert strategy.get_insertion_index([]) == 0


def test_python_strategy_skips_shebang_and_encoding() -> None:
    strategy = PythonStrategy("# File: {}")
    lines = [
        "#!/usr/bin/env python3\n",
        "# -*- coding: utf-8 -*-\n",
        "print('hello')\n",
    ]
    assert strategy.get_insertion_index(lines) == 2


def test_xml_strategy_skips_declaration() -> None:
    strategy = XmlStrategy("")
    lines = ['<?xml version="1.0"?>\n', "<root></root>\n"]
    assert strategy.get_insertion_index(lines) == 1

    lines_no_decl = ["<root></root>\n"]
    assert strategy.get_insertion_index(lines_no_decl) == 0


def test_php_strategy_skips_opentag() -> None:
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

    # Case 4: No tag (HTML)
    lines_html = ["<html>\n"]
    assert strategy.get_insertion_index(lines_html) == 0


def test_frontmatter_strategy_skips_block() -> None:
    strategy = FrontmatterStrategy("<!-- File: {} -->")

    # Case 1: Standard Frontmatter
    lines = [
        "---\n",
        "title: hello\n",
        "---\n",
        "<h1>Hi</h1>\n"
    ]
    assert strategy.get_insertion_index(lines) == 3

    # Case 2: No frontmatter
    lines_none = ["<h1>Hi</h1>\n"]
    assert strategy.get_insertion_index(lines_none) == 0

    # Case 3: Unclosed (safety check, returns 0)
    lines_unclosed = ["---\n", "title: hello\n"]
    assert strategy.get_insertion_index(lines_unclosed) == 0


def test_strategy_header_generation(tmp_path: Path) -> None:
    f = tmp_path / "test.py"
    strategy = PythonStrategy("# File: {}")
    expected = f"# File: {f.as_posix()}\n"
    assert strategy.get_expected_header(f) == expected


def test_is_header_line() -> None:
    strategy = DefaultStrategy("# File: {}")
    assert strategy.is_header_line("# File: path/to/file.py")
    assert not strategy.is_header_line("# Not a header")


def test_strategy_no_placeholder() -> None:
    # Test base class logic for styles without "{}"
    strategy = DefaultStrategy("HEADER")
    assert strategy.get_expected_header(Path("foo")) == "HEADER\n"
    assert strategy.is_header_line("HEADER")
    assert not strategy.is_header_line("OTHER")

def test_xml_strategy_empty() -> None:
    strategy = XmlStrategy("")
    assert strategy.get_insertion_index([]) == 0

def test_frontmatter_strategy_empty() -> None:
    strategy = FrontmatterStrategy("<!-- File: {} -->")
    assert strategy.get_insertion_index([]) == 0


def test_python_strategy_skips_cookie_on_second_line_no_shebang() -> None:
    strategy = PythonStrategy("# File: {}")
    lines = [
        "# Some comment\n",
        "# -*- coding: utf-8 -*-\n",
        "print('hello')\n",
    ]
    assert strategy.get_insertion_index(lines) == 2


def test_markdown_strategy_selection() -> None:
    path = Path("test.markdown")
    strategy = get_strategy_for_file(path)
    assert isinstance(strategy, FrontmatterStrategy)
    assert strategy.comment_style == "<!-- File: {} -->"


def test_frontmatter_strategy_only_frontmatter() -> None:
    strategy = FrontmatterStrategy("<!-- File: {} -->")
    # File with ONLY frontmatter
    lines = [
        "---\n",
        "title: hello\n",
        "---\n",
    ]
    # Should insert after the block (index 3)
    assert strategy.get_insertion_index(lines) == 3
