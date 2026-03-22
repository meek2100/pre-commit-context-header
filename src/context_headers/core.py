# File: src/context_headers/core.py
"""
Core file processing logic.

This module handles the file system interactions, performing checks,
strategy selection, and content modification.
"""

from __future__ import annotations
import sys
from pathlib import Path

from .config import MAX_FILE_SIZE_BYTES, ALWAYS_SKIP_FILENAMES
from .languages.factory import get_strategy_for_file

__all__ = ["process_file"]


def _write_back(path_obj: Path, content: str, filepath: str) -> bool:
    """Helper to safely write back file content, handling permission errors."""
    try:
        path_obj.write_text(content, encoding="utf-8")
        return True
    except (OSError, PermissionError) as exc:
        print(f"Skipping {filepath}: {exc}", file=sys.stderr)
        return False


def process_file(filepath: str, fix_mode: bool, remove_mode: bool = False) -> bool:
    """Processes a single file to enforce or remove context headers.

    Files are strictly read as UTF-8. Non-UTF-8 files (binary) are skipped
    silently to prevent corruption.

    Args:
        filepath: The path to the file to process.
        fix_mode: Whether to apply fixes (write changes) or just check.
        remove_mode: Whether to remove the header if found.

    Returns:
        True if the file was modified or would be modified (in check mode),
        False otherwise.
    """
    path_obj = Path(filepath)

    # 1. Mandatory Exclusion Check
    if path_obj.name in ALWAYS_SKIP_FILENAMES:
        return False

    # 2. Size Check
    try:
        if path_obj.stat().st_size > MAX_FILE_SIZE_BYTES:
            return False
    except (OSError, PermissionError):
        return False

    # 3. Strategy Selection
    strategy = get_strategy_for_file(path_obj)
    if not strategy:
        return False

    # 4. Read Content
    try:
        text_content = path_obj.read_text(encoding="utf-8")
        if text_content.startswith("\ufeff"):
            return False

        lines = text_content.splitlines(keepends=True)
    except (UnicodeDecodeError, OSError):
        return False

    # 5. Determine Insertion Point via Strategy
    insert_idx = strategy.get_insertion_index(lines)

    if insert_idx == -1:
        return False

    if lines and not lines[-1].endswith("\n"):
        lines[-1] += "\n"

    if insert_idx > len(lines):
        insert_idx = len(lines)

    # 6. Primary Header Selection & Deduplication
    primary_header_idx = -1
    check_idx = insert_idx
    while check_idx < len(lines) and not lines[check_idx].strip():
        check_idx += 1

    if check_idx < len(lines) and strategy.is_header_line(lines[check_idx]):
        primary_header_idx = check_idx

    # 7. Collect all redundant headers for removal (Constrained to preamble)
    redundant_idxs: list[int] = []

    # Calculate preamble range to prevent stripping header-shaped comments inside code body
    preamble_end = len(lines)
    for i, line in enumerate(lines):
        stripped = line.strip()
        if not stripped:
            continue
        # If it's a known comment/directive prefix or header line, consider it part of preamble
        if strategy.is_header_line(line) or any(stripped.startswith(prefix) for prefix in ("#", "//", "/*", "*", "\n# Body\n",
        encoding="utf-8",
    )

    # For removal to actually happen in core API, fix_mode must be True
    assert process_file(str(f), fix_mode=True, remove_mode=True)

    content = f.read_text()
    assert "\n---\ntitle: test\n---\nbody\n", encoding="utf-8"
    )
    assert process_file(str(md), fix_mode=True)
    assert "---\ntitle: test\n---\n\n\n", encoding="utf-8")
    assert process_file(str(only_h), fix_mode=True)  # Deduplicates to one

    # 7. Unclosed CSS
    css = tmp_path / "unsafe.css"
    css_content = "@charset 'UTF-8'\nbody {}\n"
    css.write_text(css_content, encoding="utf-8")  # No semicolon
    assert not process_file(str(css), fix_mode=True)
    assert css.read_text(encoding="utf-8") == css_content