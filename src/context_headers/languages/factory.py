# File: src/context_headers/languages/factory.py
from __future__ import annotations
from pathlib import Path

from ..config import COMMENT_STYLES
from .base import HeaderStrategy
from .strategies import (
    DefaultStrategy,
    PythonStrategy,
    ShebangStrategy,
    XmlStrategy,
)


def get_strategy_for_file(path_obj: Path) -> HeaderStrategy | None:
    """
    Factory function to return the correct strategy for a given file.
    Returns None if the file type is not supported.
    """
    # 1. Determine Extension / Type
    if path_obj.name == "Dockerfile":
        ext = ".dockerfile"
    else:
        ext = path_obj.suffix.lower()

    # 2. Get Comment Style
    style = COMMENT_STYLES.get(ext)
    if not style:
        return None

    # 3. Select Strategy
    if ext == ".py":
        return PythonStrategy(style)
    elif ext in [".xml", ".html", ".vue"]:
        # Note: HTML usually doesn't need to skip lines, but XML/Vue might
        # if they have XML declarations. XmlStrategy handles `<?xml` safely.
        return XmlStrategy(style)
    elif ext in [".sh", ".bash", ".zsh", ".rb", ".pl", ".js", ".ts"]:
        # Many scripting languages support shebangs
        return ShebangStrategy(style)

    # Fallback for others (Markdown, CSS, SQL, etc.)
    return DefaultStrategy(style)
