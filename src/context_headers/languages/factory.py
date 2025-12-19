# File: src/context_headers/languages/factory.py
"""
Factory module for creating Strategy instances.

Maps file extensions and names to specific HeaderStrategy implementations.
"""

from __future__ import annotations
from pathlib import Path

from ..config import COMMENT_STYLES
from .base import HeaderStrategy
from .strategies import (
    PythonStrategy,
    ShebangStrategy,
    XmlStrategy,
    PhpStrategy,
    FrontmatterStrategy,
)

# Extensions that need specific strategies
PYTHON_EXTS = {".py", ".pyi", ".pyw", ".pyx"}
PHP_EXTS = {".php", ".phtml", ".php3", ".php4", ".phps"}
FRONTMATTER_EXTS = {".astro", ".md", ".markdown"}
XML_EXTS = {
    ".xml",
    ".html",
    ".htm",
    ".xhtml",
    ".jhtml",
    ".vue",
    ".svelte",
    ".aspx",
    ".cshtml",
    ".jsp",
}


def get_strategy_for_file(path_obj: Path) -> HeaderStrategy | None:
    """Factory function to return the correct strategy for a given file.

    Args:
        path_obj: The pathlib.Path object of the file to check.

    Returns:
        The matching HeaderStrategy instance, or None if the file type
        is not supported in config.COMMENT_STYLES.
    """
    # 1. Determine Extension / Type
    # Handle Dockerfile and variants (case-insensitive for the main name)
    name_lower = path_obj.name.lower()
    if name_lower == "dockerfile" or name_lower.startswith("dockerfile."):
        ext = ".dockerfile"
    else:
        ext = path_obj.suffix.lower()
        # Handle dotfiles like .bashrc where suffix might be empty or misleading
        # depending on pathlib version/platform, ensure we catch the full name.
        if not ext and path_obj.name.startswith("."):
            ext = path_obj.name

    # 2. Get Comment Style
    style = COMMENT_STYLES.get(ext)
    if not style:
        return None

    # 3. Select Strategy
    if ext in PYTHON_EXTS:
        return PythonStrategy(style)

    if ext in PHP_EXTS:
        return PhpStrategy(style)

    if ext in FRONTMATTER_EXTS:
        return FrontmatterStrategy(style)

    if ext in XML_EXTS:
        return XmlStrategy(style)

    # Fallback to ShebangStrategy for all other supported types.
    # This handles shell scripts (which need shebang skipping)
    # and compiled/config languages (where checking for shebang is harmless and returns 0).
    return ShebangStrategy(style)
