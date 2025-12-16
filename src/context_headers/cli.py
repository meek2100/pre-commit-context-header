# File: src/context_headers/cli.py
from __future__ import annotations
import argparse
import sys

from .core import process_file


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
