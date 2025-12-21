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
        """Determines insertion index by skipping a Shebang line.

        Args:
            lines: List of lines in the file.

        Returns:
            1 if a Shebang is present on the first line, otherwise 0.
        """
        if not lines:
            return 0

        # Skip Shebang if on line 0
        if lines[0].startswith("#!"):
            return 1
        return 0


class DockerfileStrategy(ShebangStrategy):
    """
    Strategy for Dockerfiles.
    Skips Shebangs (Line 0) AND Parser Directives (syntax=, escape=, check=).
    Directives must be the very first lines of the file (or immediately after shebang).
    """

    def get_insertion_index(self, lines: list[str]) -> int:
        """Determines insertion index skipping parser directives."""
        # 1. Check for Shebang first (rare but handled by parent)
        idx = super().get_insertion_index(lines)

        # 2. Skip Parser Directives
        # Directives must be at the top, but can follow a shebang if valid.
        while idx < len(lines):
            line = lines[idx].strip()
            # Directive format: # directive=value
            if line.startswith("#"):
                # Normalize content to check for directive keys
                # Directives are case-insensitive.
                # Format allows spaces: # syntax = docker/dockerfile:1
                content = line[1:].strip().lower()

                # Partition at the first '=' to separate key and value
                key, sep, _ = content.partition("=")

                if sep and key.strip() in ("syntax", "escape", "check"):
                    idx += 1
                    continue

            # If we hit a non-directive line (including other comments or whitespace), we stop.
            break

        return idx


class PythonStrategy(ShebangStrategy):
    """
    Python specific strategy.
    Skips Shebangs (Line 0) AND Encoding cookies (PEP 263, Line 0 or 1).
    """

    LOOKAHEAD_LIMIT = 2

    def get_insertion_index(self, lines: list[str]) -> int:
        """Determines insertion index skipping Shebangs and encoding cookies.

        Args:
            lines: List of lines in the file.

        Returns:
            The line index after any Shebang and/or encoding cookie.
        """
        idx = super().get_insertion_index(lines)

        # Check for encoding cookie in lines [idx ... limit]
        for i in range(idx, min(len(lines), self.LOOKAHEAD_LIMIT)):
            line = lines[i].strip()
            # Regex approximation of PEP 263
            if (
                line.startswith("#")
                and "coding" in line
                and ("=" in line or ":" in line)
            ):
                return i + 1

        return idx


class DeclarationStrategy(HeaderStrategy):
    """
    Strategy for files requiring Top-of-File Declarations.
    Used for XML, HTML, CSS, Razor, and ASP/JSP.

    Skips:
    - XML declaration (<?xml ...)
    - HTML Doctype (<!DOCTYPE ...)
    - ASP/JSP directives (<%@ ...)
    - CSS Charset (@charset ...)
    - Razor Page directives (@page ...)
    """

    # Safety: Limit lookahead to avoid performance issues on massive files
    SEARCH_LIMIT = 20
    # Safety: CSS charsets must be at the very top (first few lines)
    CSS_SEARCH_LIMIT = 5

    def get_insertion_index(self, lines: list[str]) -> int:
        """Determines insertion index skipping declarations.

        Safety:
        - If the declaration spans multiple lines, we attempt to find the end.
        - If we cannot safely find the end, we return -1 (Skip).
        """
        if not lines:
            return 0

        first_line = lines[0].strip()
        lower_line = first_line.lower()

        # Check for specific declaration types
        is_tag_decl = (
            first_line.startswith("<?xml")  # <?xml ... ?>
            or lower_line.startswith("<!doctype")  # <!DOCTYPE ... >
            or first_line.startswith("<%@")  # <%@ ... %>
        )

        is_css_decl = lower_line.startswith("@charset")  # @charset "...";
        is_razor_decl = lower_line.startswith("@page")  # @page ...

        if is_tag_decl:
            # Look for closing '>'
            # Check line 0 first
            if ">" in first_line:
                return 1

            # Check subsequent lines (up to limit)
            for i in range(1, min(len(lines), self.SEARCH_LIMIT)):
                if ">" in lines[i]:
                    return i + 1

            # If not closed within limit, skip file (unsafe/ambiguous)
            return -1

        if is_css_decl:
            # Look for closing ';'
            if ";" in first_line:
                return 1
            for i in range(1, min(len(lines), self.CSS_SEARCH_LIMIT)):
                if ";" in lines[i]:
                    return i + 1
            return -1

        if is_razor_decl:
            # Razor @page is typically a single line directive ending at newline.
            return 1

        return 0


class PhpStrategy(ShebangStrategy):
    """
    PHP specific strategy.
    Skips Shebangs (Line 0) and opening PHP tags.
    """

    def get_insertion_index(self, lines: list[str]) -> int:
        """Determines insertion index skipping Shebangs and PHP open tags.

        Returns:
            The line index after the PHP open tag, if present.
            Returns -1 if no PHP tag is found, or if unsafe (XML/One-liners).
        """
        idx = super().get_insertion_index(lines)

        if idx < len(lines):
            line = lines[idx].strip()
            # Check for PHP opening tag
            if line.startswith("<?"):
                # Safety: Skip XML declarations to prevent corruption
                if line.lower().startswith("<?xml"):
                    return -1

                # Safety: Skip one-liners where the tag closes on the same line
                if "?>" in line:
                    return -1

                return idx + 1

        # If we are here, we didn't find a PHP opening tag (or it's pure HTML).
        # Inserting a `//` comment in a file that might be pure HTML
        # (interpreted by PHP engine) results in visible text on the page.
        # It is safer to SKIP this file.
        return -1


class FrontmatterStrategy(HeaderStrategy):
    """
    Strategy for files with Frontmatter (e.g. Astro, Markdown).
    Skips the frontmatter block (delimited by ---).
    """

    def get_insertion_index(self, lines: list[str]) -> int:
        """Determines insertion index by skipping YAML Frontmatter.

        Args:
            lines: List of lines in the file.

        Returns:
            The line index after the closing '---' of the frontmatter, or 0.
        """
        if not lines:
            return 0

        # Check for frontmatter start
        if lines[0].strip() == "---":
            # Find the closing fence
            for i in range(1, len(lines)):
                if lines[i].strip() == "---":
                    return i + 1

        return 0
