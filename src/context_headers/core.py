# File: src/context_headers/core.py
from __future__ import annotations
from pathlib import Path

from .config import MAX_FILE_SIZE_BYTES
from .languages.factory import get_strategy_for_file


def process_file(filepath: str, fix_mode: bool) -> bool:
    """
    Process a single file.
    Returns True if the file was modified or needs modification.
    """
    path_obj = Path(filepath)

    # 1. Size Check
    try:
        if path_obj.stat().st_size > MAX_FILE_SIZE_BYTES:
            # Silently skip large files
            return False
    except (OSError, PermissionError):
        return False

    # 2. Strategy Selection
    strategy = get_strategy_for_file(path_obj)
    if not strategy:
        return False

    expected_header = strategy.get_expected_header(path_obj)

    # 3. Read Content
    try:
        text_content = path_obj.read_text(encoding="utf-8")
        lines = text_content.splitlines(keepends=True)
    except (UnicodeDecodeError, OSError):
        return False

    # 4. Determine Insertion Point via Strategy
    insert_idx = strategy.get_insertion_index(lines)

    # Safety: Append newline to last line if missing to prevent concatenation issues
    if lines and not lines[-1].endswith("\n"):
        lines[-1] += "\n"

    # Clamp index
    insert_idx = min(insert_idx, len(lines))

    # 5. Check Status
    header_status = "missing"

    if len(lines) > insert_idx:
        current_line = lines[insert_idx]
        if current_line.strip() == expected_header.strip():
            header_status = "correct"
        elif strategy.is_header_line(current_line):
            header_status = "incorrect"

    if header_status == "correct": # pragma: no cover
        return False # pragma: no cover

    # 6. Action
    if not fix_mode:
        print(f"Missing or incorrect header: {filepath}")
        return True
    else:
        if header_status == "incorrect":
            lines[insert_idx] = expected_header
            print(f"Updated header: {filepath}")
        else:
            lines.insert(insert_idx, expected_header)
            print(f"Added header: {filepath}")

        path_obj.write_text("".join(lines), encoding="utf-8")
        return True
