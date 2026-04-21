"""CLI sub-command: envdiff pivot — show per-key view across multiple files."""
from __future__ import annotations

import argparse
import sys
from typing import List

from envdiff.differ_pivot import pivot_files
from envdiff.pivot_formatter import format_pivot_rich, format_pivot_summary


def add_pivot_subparser(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser(
        "pivot",
        help="Pivot diff: show every key and its value across all files.",
    )
    p.add_argument("files", nargs="+", metavar="FILE", help=".env files to compare")
    p.add_argument(
        "--show-values",
        action="store_true",
        default=False,
        help="Print actual values instead of masking them.",
    )
    p.add_argument(
        "--conflicts-only",
        action="store_true",
        default=False,
        help="Only display keys that differ across files.",
    )
    p.add_argument(
        "--summary",
        action="store_true",
        default=False,
        help="Print a one-line summary instead of the full table.",
    )
    p.set_defaults(func=_run)


def _run(args: argparse.Namespace) -> int:
    if len(args.files) < 2:
        print("pivot requires at least two files.", file=sys.stderr)
        return 2

    result = pivot_files(args.files)

    if args.summary:
        print(format_pivot_summary(result))
    else:
        print(
            format_pivot_rich(
                result,
                show_values=args.show_values,
                only_conflicts=args.conflicts_only,
            )
        )
        print()
        print(format_pivot_summary(result))

    has_issues = bool(result.conflicted_rows() or result.missing_rows())
    return 1 if has_issues else 0


def main(argv: List[str] | None = None) -> None:
    parser = argparse.ArgumentParser(prog="envdiff-pivot")
    subs = parser.add_subparsers()
    add_pivot_subparser(subs)
    args = parser.parse_args(argv)
    if not hasattr(args, "func"):
        parser.print_help()
        sys.exit(2)
    sys.exit(args.func(args))
