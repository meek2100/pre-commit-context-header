# File: src/context_headers/languages/strategies.py
from __future__ import annotations
from .base import HeaderStrategy


class ShebangStrategy(HeaderStrategy):
    """
    Strategy for scripts that might have a Shebang (#!...) on the first line.
    Used for Shell, Ruby, Perl, Node.js, etc.
    Also acts as the default strategy (inserts at 0 if no shebang found).
    """

    def get_insertion_index(self, lines: list[str]) -> int:
        if not lines:
            return 0

        # Skip Shebang if on line 0
        if lines[0].startswith("#!"):
            return 1
        return 0


class PythonStrategy(ShebangStrategy):
    """
    Python specific strategy.
    Skips Shebangs (Line 0) AND Encoding cookies (PEP 263, Line 0 or 1).
    """

    def get_insertion_index(self, lines: list[str]) -> int:
        idx = super().get_insertion_index(lines)

        # Check for encoding cookie in lines [idx ... 1]
        # Max line to check is index 1 (second line).
        check_limit = 2

        for i in range(idx, min(len(lines), check_limit)):
            line = lines[i].strip()
            # Regex approximation of PEP 263
            if (
                line.startswith("#")
                and "coding" in line
                and ("=" in line or ":" in line)
            ):
                return i + 1

        return idx


class XmlStrategy(HeaderStrategy):
    """
    Strategy for XML-like files.
    Skips XML declaration (<?xml ... ?>) on the first line.
    """

    def get_insertion_index(self, lines: list[str]) -> int:
        if not lines:
            return 0

        if lines[0].strip().startswith("<?xml"):
            return 1
        return 0


class PhpStrategy(ShebangStrategy):
    """
    PHP specific strategy.
    Skips Shebangs (Line 0) and opening PHP tags (<?php or <?) on line 0 or 1.
    """

    def get_insertion_index(self, lines: list[str]) -> int:
        idx = super().get_insertion_index(lines)

        if idx < len(lines):
            line = lines[idx].strip()
            # Check for PHP opening tag
            if line.startswith("<?"):
                return idx + 1
        return idx


class FrontmatterStrategy(HeaderStrategy):
    """
    Strategy for files with Frontmatter (e.g. Astro, Markdown).
    Skips the frontmatter block (delimited by ---).
    """

    def get_insertion_index(self, lines: list[str]) -> int:
        if not lines:
            return 0

        # Check for frontmatter start
        if lines[0].strip() == "---":
            # Find the closing fence
            for i in range(1, len(lines)):
                if lines[i].strip() == "---":
                    return i + 1

        return 0
