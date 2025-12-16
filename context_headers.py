#!/usr/bin/env python3
"""
Universal utility to check or enforce file headers (banners).

Usage:
    context-headers file1.py file2.js
    context-headers --fix file1.py file2.js
"""

import argparse
import sys
from pathlib import Path

# Safety: Do not process files larger than this (1MB) to prevent hangs.
MAX_FILE_SIZE_BYTES = 1024 * 1024

# Configuration: Comment styles for various extensions.
COMMENT_STYLES = {
    # Scripting / Config
    ".py": "# File: {}",
    ".yaml": "# File: {}",
    ".yml": "# File: {}",
    ".sh": "# File: {}",
    ".toml": "# File: {}",
    ".tf": "# File: {}",
    ".dockerfile": "# File: {}",
    ".rb": "# File: {}",
    ".pl": "# File: {}",
    # Web / JS
    ".js": "// File: {}",
    ".ts": "// File: {}",
    ".jsx": "// File: {}",
    ".tsx": "// File: {}",
    ".css": "/* File: {} */",
    ".scss": "/* File: {} */",
    ".less": "/* File: {} */",
    # Compiled / Systems
    ".java": "// File: {}",
    ".kt": "// File: {}",
    ".rs": "// File: {}",
    ".go": "// File: {}",
    ".c": "// File: {}",
    ".cpp": "// File: {}",
    ".h": "// File: {}",
    ".hpp": "// File: {}",
    ".cs": "// File: {}",
    ".swift": "// File: {}",
    # HTML / Markdown / XML (Using visible comments)
    ".html": "",
    ".md": "",
    ".xml": "",
    ".vue": "",
}


def get_expected_header(filepath: Path) -> str | None:
    """Generate the expected header string based on file extension."""
    if filepath.name == "Dockerfile":
        ext = ".dockerfile"
    else:
        ext = filepath.suffix.lower()

    if ext not in COMMENT_STYLES:
        return None

    clean_path = filepath.as_posix()
    return COMMENT_STYLES[ext].format(clean_path) + "\n"


def is_header_line(line: str, extension: str) -> bool:
    """Check if a line looks like a context header for the given extension."""
    style = COMMENT_STYLES.get(extension)
    if not style:
        return False

    if "{}" in style:
        prefix, suffix = style.split("{}", 1)
    else:
        prefix, suffix = style, ""

    stripped_line = line.strip()
    return stripped_line.startswith(prefix.strip()) and stripped_line.endswith(
        suffix.strip()
    )


def get_insertion_index(lines: list[str]) -> int:
    """
    Determine the safe insertion index.
    Skips Shebangs (#!...) and Python Encoding cookies (coding=...).
    """
    idx = 0
    if not lines:
        return 0

    # 1. Skip Shebang
    if lines[idx].startswith("#!"):
        idx += 1

    # 2. Skip Encoding Cookie (PEP 263)
    # Must be on line 1 or 2. If we passed a shebang, we are at line 2.
    if idx < len(lines):
        line = lines[idx].strip()
        # Regex approximation of PEP 263
        if line.startswith("#") and "coding" in line and ("=" in line or ":" in line):
            idx += 1

    return idx


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
    except OSError:
        return False

    # 2. Extension Check
    if path_obj.name == "Dockerfile":
        ext = ".dockerfile"
    else:
        ext = path_obj.suffix.lower()

    expected_header = get_expected_header(path_obj)
    if not expected_header:
        return False

    # 3. Read Content
    try:
        text_content = path_obj.read_text(encoding="utf-8")
        lines = text_content.splitlines(keepends=True)
    except (UnicodeDecodeError, OSError):
        return False

    if not lines:
        return False

    # 4. Determine Insertion Point
    insert_idx = get_insertion_index(lines)

    # Safety: Append newline to last line if missing, to prevent concatenation issues
    if lines and not lines[-1].endswith("\n"):
        lines[-1] += "\n"

    # Handle case where file is only shebangs/cookies
    if insert_idx > len(lines):
        insert_idx = len(lines)

    # 5. Check Status
    header_status = "missing"

    if len(lines) > insert_idx:
        current_line = lines[insert_idx]
        if current_line.strip() == expected_header.strip():
            header_status = "correct"
        elif is_header_line(current_line, ext):
            header_status = "incorrect"

    if header_status == "correct":
        return False

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


def main() -> None:
    parser = argparse.ArgumentParser(description="Enforce file path headers.")
    parser.add_argument(
        "--fix", action="store_true", help="Automatically add or update headers."
    )
    parser.add_argument("filenames", nargs="*", help="Files to check.")
    args = parser.parse_args()

    files_impacted = 0
    for f in args.filenames:
        if process_file(f, args.fix):
            files_impacted += 1

    if files_impacted > 0:
        if args.fix:
            print(f"\n{files_impacted} files were updated with headers.")
            sys.exit(1)
        else:
            print(
                f"\n{files_impacted} files have missing/incorrect headers. Run with --fix."
            )
            sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()
