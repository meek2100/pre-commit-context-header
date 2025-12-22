# File: src/context_headers/cli.py
"""
Command-line interface entry point.

Handles argument parsing and orchestrates file processing.
"""

from __future__ import annotations
import argparse
import sys

from .core import process_file

__all__ = ["run", "main"]


def run(argv: list[str] | None = None) -> int:
    """Executes the CLI application.

    Args:
        argv: List of command-line arguments. Defaults to None (uses sys.argv).

    Returns:
        0 if successful (no changes needed or help displayed),
        1 if changes were made or errors occurred.
    """
    parser = argparse.ArgumentParser(description="Enforce file path headers.")
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--fix", action="store_true", help="Automatically add or update headers."
    )
    group.add_argument(
        "--remove", action="store_true", help="Remove context headers from files."
    )
    parser.add_argument("filenames", nargs="*", help="Files to check.")
    args = parser.parse_args(argv)

    files_impacted = 0
    for f in args.filenames:
        if process_file(f, fix_mode=args.fix, remove_mode=args.remove):
            files_impacted += 1

    if files_impacted > 0:
        if args.fix:
            print(f"\n{files_impacted} files were updated with headers.")
            return 1
        elif args.remove:
            print(f"\n{files_impacted} files had headers removed.")
            return 1
        else:
            print(
                f"\n{files_impacted} files have missing/incorrect headers. Run with --fix."
            )
            return 1

    return 0


def main() -> None:
    sys.exit(run(sys.argv[1:]))
