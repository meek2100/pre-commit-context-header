# File: tests/languages/test_strategies.py
import pytest
from pathlib import Path
from context_headers.languages.strategies import (
    DefaultStrategy,
    ShebangStrategy,
    PythonStrategy,
    XmlStrategy,
)


def test_default_strategy_insertion() -> None:
    strategy = DefaultStrategy("/* File: {} */")
    lines = ["body { color: red; }\n"]
    assert strategy.get_insertion_index(lines) == 0


def test_shebang_strategy_skips_shebang() -> None:
    strategy = ShebangStrategy("# File: {}")
    lines = ["#!/bin/bash\n", "echo 'hello'\n"]
    assert strategy.get_insertion_index(lines) == 1


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


def test_strategy_header_generation(tmp_path: Path) -> None:
    f = tmp_path / "test.py"
    strategy = PythonStrategy("# File: {}")
    expected = f"# File: {f.as_posix()}\n"
    assert strategy.get_expected_header(f) == expected


def test_is_header_line() -> None:
    strategy = DefaultStrategy("# File: {}")
    assert strategy.is_header_line("# File: path/to/file.py")
    assert not strategy.is_header_line("# Not a header")
