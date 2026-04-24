"""CLI sub-command: envdiff radar – show radar profile for env files."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from envdiff.differ import diff_pair
from envdiff.differ_radar import build_radar
from envdiff.radar_formatter import format_radar_rich, format_radar_summary


def add_radar_subparser(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser(
        "radar",
        help="Show a radar / spider-chart profile comparing env files.",
    )
    p.add_argument("base", help="Base .env file")
    p.add_argument("targets", nargs="+", help="One or more target .env files")
    p.add_argument(
        "--check-values",
        action="store_true",
        default=False,
        help="Include value-mismatch in consistency axis.",
    )
    p.add_argument(
        "--summary",
        action="store_true",
        default=False,
        help="Print a single-line summary instead of full output.",
    )
    p.set_defaults(func=_run)


def _run(args: argparse.Namespace) -> int:
    base_path = Path(args.base)
    if not base_path.exists():
        print(f"error: base file not found: {base_path}", file=sys.stderr)
        return 2

    diffs = []
    for t in args.targets:
        target_path = Path(t)
        if not target_path.exists():
            print(f"error: target file not found: {target_path}", file=sys.stderr)
            return 2
        diffs.append(diff_pair(base_path, target_path, check_values=args.check_values))

    result = build_radar(diffs)

    if args.summary:
        print(format_radar_summary(result))
    else:
        print(format_radar_rich(result))

    worst = min((e.overall for e in result.entries), default=1.0)
    return 0 if worst >= 1.0 else 1


def main() -> None:
    parser = argparse.ArgumentParser(prog="envdiff-radar")
    subs = parser.add_subparsers()
    add_radar_subparser(subs)
    args = parser.parse_args()
    if not hasattr(args, "func"):
        parser.print_help()
        sys.exit(0)
    sys.exit(args.func(args))
