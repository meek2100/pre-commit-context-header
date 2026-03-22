# File: src/context_headers/languages/strategies.py
"""
Specific strategy implementations for different languages.

Contains logic for handling language-specific syntax like Shebangs,
XML declarations, Frontmatter, etc.
"""

from __future__ import annotations
from .base import HeaderStrategy


class ShebangStrategy(HeaderStrategy):
    """
    Strategy for scripts that might have a Shebang (#!...) on the first line.
    Used for Shell, Ruby, Perl, Node.js, etc.
    Also acts as the default strategy (inserts at 0 if no Shebang found).
    """

    def get_insertion_index(self, lines: list[str]) -> int:
        """Determines insertion index skipping any existing headers to find a Shebang.

        Args:
            lines: List of lines in the file.

        Returns:
            The line index after a Shebang if one exists (even if preceded by headers).
            Returns 0 if no Shebang is found.
        """
        if not lines:
            return 0

        idx = 0
        while idx < len(lines) and self.is_header_line(lines[idx]):
            idx += 1

        if idx < len(lines) and lines[idx].startswith("#!"):
            return idx + 1

        # If no shebang was found underneath headers, the earliest valid spot is 0.
        return 0


class DockerfileStrategy(ShebangStrategy):
    """
    Strategy for Dockerfiles.
    Skips Shebangs (Line 0) AND Parser Directives (syntax=, escape=, check=).
    Directives must be the very first lines of the file (or immediately after shebang).
    """

    def get_insertion_index(self, lines: list[str]) -> int:
        """Determines insertion index skipping headers, shebangs, and directives."""
        # 1. Start by finding the end of headers + shebang
        idx = 0
        while idx < len(lines) and self.is_header_line(lines[idx]):
            idx += 1

        if idx < len(lines) and lines[idx].startswith("#!"):
            idx += 1

        # 2. Skip Parser Directives
        # Directives must be near the top.
        while idx < len(lines):
            line = lines[idx].strip()
            # Directive format: # directive=value
            if line.startswith("#"):
                # Normalize content to check for directive keys
                content = line[1:].strip().lower()
                key, sep, _ = content.partition("=")
                if sep and key.strip() in ("syntax", "escape", "check"):
                    idx += 1
                    continue
            break

        # If we skipped anything, that's our base index.
        # But if we were at the very top (only headers), return 0.
        # Wait, if we only had headers, idx is now > 0.
        # If we only had headers, we want to return 0.

        # Check if we actually skipped a directive or shebang
        discovered_skip = False
        scan_idx = 0
        while scan_idx < len(lines) and self.is_header_line(lines[scan_idx]):
            scan_idx += 1
        if scan_idx < idx:
            discovered_skip = True

        return idx if discovered_skip else 0


class PythonStrategy(ShebangStrategy):
    """
    Python specific strategy.
    Skips Shebangs (Line 0) AND Encoding cookies (PEP 263, Line 0 or 1).
    """

    LOOKAHEAD_LIMIT = 2

    def get_insertion_index(self, lines: list[str]) -> int:
        """Determines insertion index skipping headers, shebangs, and encoding cookies."""
        # 1. Find end of headers + shebang
        base_idx = 0
        while base_idx < len(lines) and self.is_header_line(lines[base_idx]):
            base_idx += 1

        has_shebang = False
        if base_idx < len(lines) and lines[base_idx].startswith("#!"):
            base_idx += 1
            has_shebang = True

        # 2. Check for encoding cookie in subsequent lines
        idx = base_idx
        limit = min(len(lines), idx + self.LOOKAHEAD_LIMIT)
        has_cookie = False
        for i in range(idx, limit):
            line = lines[i].strip()
            if (
                line.startswith("#")
                and "coding" in line
                and ("=" in line or ":" in line)
            ):
                idx = i + 1
                has_cookie = True
                break

        return idx if (has_shebang or has_cookie) else 0


class DeclarationStrategy(HeaderStrategy):
    """
    Strategy for files requiring Top-of-File Declarations.
    Used for XML, HTML, CSS, Razor, and ASP/JSP.
    """

    SEARCH_LIMIT = 20
    CSS_SEARCH_LIMIT = 5

    def get_insertion_index(self, lines: list[str]) -> int:
        """Determines insertion index skipping headers and declarations."""
        if not lines:
            return 0

        idx = 0
        while idx < len(lines) and self.is_header_line(lines[idx]):
            idx += 1

        if idx >= len(lines):
            return 0

        first_line = lines[idx].strip()
        lower_line = first_line.lower()

        # Check for specific declaration types
        is_tag_decl = (
            first_line.startswith("<?xml")
            or lower_line.startswith("<!doctype")
            or first_line.startswith("<%@")
        )
        is_css_decl = lower_line.startswith("@charset")
        is_razor_decl = lower_line.startswith("@page")

        if is_tag_decl:
            if ">" in first_line:
                return idx + 1
            for i in range(idx + 1, min(len(lines), idx + self.SEARCH_LIMIT)):
                if ">" in lines[i]:
                    return i + 1
            return -1

        if is_css_decl:
            if ";" in first_line:
                return idx + 1
            for i in range(idx + 1, min(len(lines), idx + self.CSS_SEARCH_LIMIT)):
                if ";" in lines[i]:
                    return i + 1
            return -1

        if is_razor_decl:
            return idx + 1

        return 0


class PhpStrategy(ShebangStrategy):
    """
    PHP specific strategy.
    Skips Shebangs (Line 0) and opening PHP tags.
    """

    def get_insertion_index(self, lines: list[str]) -> int:
        """Determines insertion index skipping headers, shebangs, and PHP open tags."""
        # 1. Find end of headers + shebang
        idx = 0
        while idx < len(lines) and self.is_header_line(lines[idx]):
            idx += 1

        if idx < len(lines) and lines[idx].startswith("#!"):
            idx += 1

        if idx < len(lines):
            line = lines[idx].strip()
            if line.startswith("<?"):
                if line.lower().startswith("<?xml") or "?>" in line:
                    return -1
                return idx + 1

        return -1


class FrontmatterStrategy(HeaderStrategy):
    """
    Strategy for files with Frontmatter (e.g. Astro, Markdown).
    Skips the frontmatter block (delimited by ---).
    """

    def get_insertion_index(self, lines: list[str]) -> int:
        """Determines insertion index skipping headers and YAML Frontmatter."""
        if not lines:
            return 0

        idx = 0
        while idx < len(lines) and self.is_header_line(lines[idx]):
            idx += 1

        if idx < len(lines) and lines[idx].strip() == "---":
            for i in range(idx + 1, len(lines)):
                if lines[i].strip() == "---":
                    return i + 1
            return -1

        return 0
