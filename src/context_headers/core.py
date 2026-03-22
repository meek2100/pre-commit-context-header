# File: src/context_headers/core.py
"""
Core file processing logic.

This module handles the file system interactions, performing checks,
strategy selection, and content modification.
"""

from __future__ import annotations
from pathlib import Path

from .config import MAX_FILE_SIZE_BYTES, ALWAYS_SKIP_FILENAMES
from .languages.factory import get_strategy_for_file

__all__ = ["process_file"]


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
    # Safety: Skip known lockfiles and other forbidden files immediately.
    # This takes precedence over size or extension checks.
    if path_obj.name in ALWAYS_SKIP_FILENAMES:
        return False

    # 2. Size Check
    try:
        if path_obj.stat().st_size > MAX_FILE_SIZE_BYTES:
            # Silently skip large files
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

        # Safety: Check for Byte Order Mark (BOM).
        # If present, prepending data corrupts the file. We must skip.
        if text_content.startswith("\ufeff"):
            return False

        lines = text_content.splitlines(keepends=True)
    except (UnicodeDecodeError, OSError):
        return False

    # 5. Determine Insertion Point via Strategy
    insert_idx = strategy.get_insertion_index(lines)

    # Safety: Strategy requested skip (e.g., ambiguous PHP/HTML)
    if insert_idx == -1:
        return False

    # Safety: Append newline to last line if missing to prevent concatenation issues
    if lines and not lines[-1].endswith("\n"):
        lines[-1] += "\n"

    # Clamp index
    if insert_idx > len(lines):
        insert_idx = len(lines)

    # 6. Primary Header Selection & Deduplication
    # We look for a "primary" header starting from our ideal insertion point,
    # skipping empty lines. Any other header found in the file is considered redundant.
    primary_header_idx = -1
    check_idx = insert_idx
    while check_idx < len(lines) and not lines[check_idx].strip():
        check_idx += 1

    if check_idx < len(lines) and strategy.is_header_line(lines[check_idx]):
        primary_header_idx = check_idx

    # 7. Collect all redundant headers for removal
    redundant_idxs: list[int] = []
    for i, line in enumerate(lines):
        if strategy.is_header_line(line) and i != primary_header_idx:
            redundant_idxs.append(i)

    # 8. Remove Mode Logic
    if remove_mode:
        all_to_remove: list[int] = sorted(
            redundant_idxs + ([primary_header_idx] if primary_header_idx != -1 else []),
            reverse=True,
        )
        if not all_to_remove:
            return False

        # Safety: Remove mode ALWAYS applies changes if called via API,
        # following the original tool's behavior, but we still respect fix_mode
        # for consistent reporting if we ever want a "remove-check" mode.
        if fix_mode:
            for i in all_to_remove:
                lines.pop(i)
            path_obj.write_text("".join(lines), encoding="utf-8")
            print(f"Removed headers: {filepath}")
        else:
            print(f"Would remove headers: {filepath}")
        return True

    # 9. Fix/Check Mode Decisions
    expected_header = strategy.get_expected_header(path_obj)
    header_status = "missing"

    if primary_header_idx != -1:
        if lines[primary_header_idx].strip() == expected_header.strip():
            header_status = "correct"
        else:
            header_status = "incorrect"

    needs_dedup = len(redundant_idxs) > 0
    if header_status == "correct" and not needs_dedup:
        return False

    # 10. Action
    if not fix_mode:
        reason = "Missing or incorrect header"
        if needs_dedup and header_status == "correct":
            reason = "Duplicate headers"
        elif needs_dedup:
            reason = "Incorrect and duplicate headers"
        print(f"{reason}: {filepath}")
        return True

    # Apply Fixes:
    # 1. Remove redundant headers first (reverse order)
    for i in sorted(redundant_idxs, reverse=True):
        lines.pop(i)
        # Shift primary_header_idx if we removed a line before it
        if primary_header_idx != -1 and i < primary_header_idx:
            primary_header_idx -= 1
        # Shift insert_idx if we removed a line before it
        if i < insert_idx:
            insert_idx -= 1

    # 2. Update or Insert
    if primary_header_idx != -1:
        lines[primary_header_idx] = expected_header
        if needs_dedup:
            print(f"Updated header and removed duplicates: {filepath}")
        else:
            print(f"Updated header: {filepath}")
    else:
        # Insert at the originally calculated ideal spot
        lines.insert(insert_idx, expected_header)
        if needs_dedup:
            print(f"Added header and removed duplicates: {filepath}")
        else:
            print(f"Added header: {filepath}")

    path_obj.write_text("".join(lines), encoding="utf-8")
    return True
