# File: src/context_headers/languages/base.py
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
        """Check if a line looks like a context header."""
        if "{}" in self.comment_style:
            prefix, suffix = self.comment_style.split("{}", 1)
        else:
            prefix, suffix = self.comment_style, ""

        stripped = line.strip()
        return stripped.startswith(prefix.strip()) and stripped.endswith(suffix.strip())

    @abstractmethod
    def get_insertion_index(self, lines: list[str]) -> int:
        """
        Determine the safe insertion index (line number).
        Should skip things like Shebangs or XML declarations.
        """
        pass  # pragma: no cover
