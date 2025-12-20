# File: src/context_headers/languages/base.py
"""
Base classes for header strategies.

Defines the interface and common logic for detecting and inserting
headers across different language types.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from pathlib import Path


class HeaderStrategy(ABC):
    """
    Abstract base class for language-specific header insertion logic.
    """

    def __init__(self, comment_style: str) -> None:
        self.comment_style = comment_style

    def get_expected_header(self, filepath: Path) -> str:
        """Generate the expected header string."""
        clean_path = filepath.as_posix()
        return self.comment_style.format(clean_path) + "\n"

    def is_header_line(self, line: str) -> bool:
        """Check if a line looks like a context header.

        This method includes global safety checks to ensure Shebangs
        are never misidentified as headers, and that empty styles don't
        result in false positives.
        """
        # Safety: A Shebang line is NEVER a context header.
        if line.startswith("#!"):
            return False

        # Safety: If comment style is empty, it would match everything.
        if not self.comment_style:
            return False

        if "{}" in self.comment_style:
            prefix, suffix = self.comment_style.split("{}", 1)
        else:
            prefix, suffix = self.comment_style, ""

        # Safety: If both prefix and suffix are empty/whitespace,
        # the pattern matches *everything*. This is dangerous.
        if not prefix.strip() and not suffix.strip():
            return False

        stripped = line.strip()
        return stripped.startswith(prefix.strip()) and stripped.endswith(suffix.strip())

    @abstractmethod
    def get_insertion_index(self, lines: list[str]) -> int:
        """
        Determine the safe insertion index (line number).
        Should skip things like Shebangs or XML declarations.
        Returns -1 if the file should be skipped (e.g. ambiguous content).
        """
        raise NotImplementedError
