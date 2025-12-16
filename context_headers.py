#!/usr/bin/env python3
"""
Universal utility to check or enforce file headers (banners).

Usage:
    context-headers file1.py file2.js
    context-headers --fix file1.py file2.js
"""

import argparse
import os
import sys

# Configuration: Comment styles for various extensions.
# We include "File:" in the template to act as a marker.
# This allows us to distinguish our headers from normal comments.
COMMENT_STYLES = {
    # Scripting / Config
    ".py": "# File: {}",
    ".yaml": "# File: {}",
    ".yml": "# File: {}",
    ".sh": "# File: {}",
    ".toml": "# File: {}",
    # Web / JS
    ".js": "// File: {}",
    ".ts": "// File: {}",
    ".jsx": "// File: {}",
    ".tsx": "// File: {}",
    ".css": "/* File: {} */",
    ".scss": "/* File: {} */",
    # HTML / Markdown (Use HTML comments which are invisible in render)
    ".html": "",
    ".md": "",
    ".xml": "",
    # Compiled / Systems
    ".c": "// File: {}",
    ".cpp": "// File: {}",
    ".h": "// File: {}",
    ".hpp": "// File: {}",
    ".java": "// File: {}",
    ".rs": "// File: {}",
    ".go": "// File: {}",
}

# Safety Net: Files/Dirs to ignore
SKIP_FILES = {"package.json", "package-lock.json", ".DS_Store", "LICENSE"}


def get_expected_header(filepath: str) -> str | None:
    """Generate the expected header string based on file extension."""
    _, ext = os.path.splitext(filepath)

    # Check strict match first, then case-insensitive
    if ext not in COMMENT_STYLES:
        return None

    # Normalize to forward slashes for consistency across OS
    clean_path = filepath.replace("\\", "/")

    # Strip leading './' if present
    if clean_path.startswith("./"):
        clean_path = clean_path[2:]

    return COMMENT_STYLES[ext].format(clean_path) + "\n"


def is_header_line(line: str, extension: str) -> bool:
    """
    Check if a line looks like a context header for the given extension.
    It checks if the line matches the pattern of the comment style,
    ignoring the actual path content.
    """
    style = COMMENT_STYLES.get(extension)
    if not style:
        return False

    # Split template into prefix and suffix (e.g., "/* File: " and " */")
    if "{}" in style:
        prefix, suffix = style.split("{}", 1)
    else:
        prefix, suffix = style, ""

    stripped_line = line.strip()
    return stripped_line.startswith(prefix.strip()) and stripped_line.endswith(
        suffix.strip()
    )


def process_file(filepath: str, fix_mode: bool) -> bool:
    """
    Process a single file.
    Returns True if the file was modified or needs modification (in check mode).
    """
    filename = os.path.basename(filepath)
    if filename in SKIP_FILES:
        return False

    _, ext = os.path.splitext(filepath)
    expected_header = get_expected_header(filepath)
    if not expected_header:
        # File type not supported
        return False

    try:
        with open(filepath, encoding="utf-8") as f:
            lines = f.readlines()
    except (UnicodeDecodeError, OSError):
        # Skip binary files or unreadable files
        return False

    # 1. Determine insertion point (skip Shebangs)
    insert_idx = 0
    if lines and lines[0].startswith("#!"):
        insert_idx = 1

    # 2. Analyze existing state
    # We look at the line where the header *should* be.
    header_status = "missing"  # options: correct, incorrect, missing

    if len(lines) > insert_idx:
        current_line = lines[insert_idx]

        # Check if it matches the EXACT expected header
        if current_line.strip() == expected_header.strip():
            header_status = "correct"
        # Check if it looks like an OLD/WRONG header (pattern match)
        elif is_header_line(current_line, ext):
            header_status = "incorrect"

    if header_status == "correct":
        return False

    # 3. Action based on mode
    if not fix_mode:
        print(f"Missing or incorrect header: {filepath}")
        return True
    else:
        if header_status == "incorrect":
            # Update the existing line
            lines[insert_idx] = expected_header
            print(f"Updated header: {filepath}")
        else:
            # Insert a new line
            lines.insert(insert_idx, expected_header)
            print(f"Added header: {filepath}")

        with open(filepath, "w", encoding="utf-8") as f:
            f.writelines(lines)
        return True


def main() -> None:
    parser = argparse.ArgumentParser(description="Enforce file path headers.")
    parser.add_argument(
        "--fix", action="store_true", help="Automatically add or update headers."
    )
    parser.add_argument("filenames", nargs="*", help="Files to check.")
    args = parser.parse_args()

    files_impacted = 0
    for filepath in args.filenames:
        if process_file(filepath, args.fix):
            files_impacted += 1

    if files_impacted > 0:
        if args.fix:
            print(f"\n{files_impacted} files were updated with headers.")
            # Exit 1 so pre-commit framework knows changes were made
            sys.exit(1)
        else:
            print(
                f"\n{files_impacted} files have missing/incorrect headers. Run with --fix."
            )
            sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()
