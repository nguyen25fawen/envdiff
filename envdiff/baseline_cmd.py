"""CLI sub-command: baseline — compare targets against a base env file."""
from __future__ import annotations

import argparse
import sys
from typing import List

from envdiff.baseline import compare_against_base
from envdiff.baseline_formatter import format_baseline_result, format_baseline_summary


def add_baseline_subparser(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser(
        "baseline",
        help="Compare one or more env files against a base file.",
    )
    p.add_argument("base", help="Base .env file to compare against.")
    p.add_argument("targets", nargs="+", help="Target .env files to compare.")
    p.add_argument(
        "--check-values",
        action="store_true",
        default=False,
        help="Also flag value mismatches (not just missing keys).",
    )
    p.add_argument(
        "--show-values",
        action="store_true",
        default=False,
        help="Display actual values in output (default: masked).",
    )
    p.add_argument(
        "--summary",
        action="store_true",
        default=False,
        help="Print only the summary line.",
    )
    p.set_defaults(func=_run)


def _run(args: argparse.Namespace) -> int:
    result = compare_against_base(
        base_path=args.base,
        target_paths=args.targets,
        check_values=args.check_values,
    )
    if args.summary:
        print(format_baseline_summary(result))
    else:
        print(format_baseline_result(result, show_values=args.show_values))
        print()
        print(format_baseline_summary(result))
    return 1 if result.any_differences() else 0


def main(argv: List[str] | None = None) -> None:
    parser = argparse.ArgumentParser(prog="envdiff baseline")
    subs = parser.add_subparsers()
    add_baseline_subparser(subs)
    args = parser.parse_args(argv)
    if not hasattr(args, "func"):
        parser.print_help()
        sys.exit(0)
    sys.exit(args.func(args))
