"""CLI helpers for the interpolate sub-command."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .parser import parse_env_file
from .interpolator import interpolate
from .interpolation_formatter import format_interpolation_result, format_interpolation_summary


def add_interpolate_subparser(subparsers: argparse._SubParsersAction) -> None:  # noqa: SLF001
    p = subparsers.add_parser(
        "interpolate",
        help="Detect and resolve $VAR / ${VAR} references in a .env file.",
    )
    p.add_argument("file", help="Path to the .env file to analyse.")
    p.add_argument(
        "--show-resolved",
        action="store_true",
        default=False,
        help="Print the resolved value for each interpolated key.",
    )
    p.add_argument(
        "--summary",
        action="store_true",
        default=False,
        help="Print a one-line summary instead of the full report.",
    )
    p.set_defaults(func=_run)


def _run(args: argparse.Namespace) -> int:
    path = Path(args.file)
    if not path.exists():
        print(f"error: file not found: {path}", file=sys.stderr)
        return 2

    env = parse_env_file(path)
    result = interpolate(env)

    if args.summary:
        print(format_interpolation_summary(result))
    else:
        print(format_interpolation_result(result, show_resolved=args.show_resolved))

    return 1 if result.unresolved else 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="envdiff-interpolate")
    subs = parser.add_subparsers()
    add_interpolate_subparser(subs)
    args = parser.parse_args(argv)
    if not hasattr(args, "func"):
        parser.print_help()
        return 0
    return args.func(args)
