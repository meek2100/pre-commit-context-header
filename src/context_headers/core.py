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

        # 7. Calculate preamble range to prevent stripping header-shaped comments inside code body
        if (
            strategy.is_header_line(line)
            or stripped == "---"
            or any(
                stripped.startswith(p)
                for p in ("#", "//", "/", "'''", '"""', "REM", "/*")
            )
        ):
            continue

        # Stop at the first non-header, non-comment line
        preamble_end = i
        break

    # 8. Collect all redundant headers for removal (Constrained to preamble)
    for i in range(preamble_end):
        if strategy.is_header_line(lines[i]) and i != primary_header_idx:
            redundant_idxs.append(i)

    # 9. Modification Check
    expected_header = strategy.get_expected_header(path_obj)
    needs_insertion = False
    needs_removal = bool(redundant_idxs)

    if remove_mode:
        if primary_header_idx != -1:
            redundant_idxs.append(primary_header_idx)
            needs_removal = True
    else:
        # We need a header. Is the primary one correct?
        if primary_header_idx == -1 or lines[primary_header_idx] != expected_header:
            needs_insertion = True
            if primary_header_idx != -1:
                redundant_idxs.append(primary_header_idx)
                needs_removal = True

    if not (needs_insertion or needs_removal):
        return False

    # 10. Apply Fixes or Report
    if not fix_mode:
        msg = (
            "Missing or incorrect header"
            if not remove_mode
            else "Extraneous header found"
        )
        print(f"{msg}: {filepath}")
        return True

    # Apply removals in reverse order to keep indices valid
    for idx in sorted(set(redundant_idxs), reverse=True):
        lines.pop(idx)
        # If we remove a line BEFORE the insertion point, the insertion point moves up.
        if not remove_mode and idx < insert_idx:
            insert_idx -= 1

    if needs_insertion and not remove_mode:
        lines.insert(insert_idx, expected_header)

    return _write_back(path_obj, "".join(lines), filepath)
