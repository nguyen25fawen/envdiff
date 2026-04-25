"""CLI subcommand: envdiff topology."""
from __future__ import annotations

import argparse
import sys

from envdiff.differ_topology import build_topology
from envdiff.topology_formatter import format_topology_rich, format_topology_summary


def add_topology_subparser(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser(
        "topology",
        help="Map structural relationships between .env files.",
    )
    p.add_argument("files", nargs="+", metavar="FILE", help="Two or more .env files.")
    p.add_argument(
        "--show-shared",
        action="store_true",
        default=False,
        help="List shared keys for each pair.",
    )
    p.add_argument(
        "--summary",
        action="store_true",
        default=False,
        help="Print one-line summary only.",
    )
    p.set_defaults(func=_run)


def _run(args: argparse.Namespace) -> int:
    if len(args.files) < 2:
        print("topology requires at least two files.", file=sys.stderr)
        return 2

    result = build_topology(args.files)

    if args.summary:
        print(format_topology_summary(result))
    else:
        print(format_topology_rich(result, show_shared=args.show_shared))

    return 0


def main() -> None:  # pragma: no cover
    parser = argparse.ArgumentParser(prog="envdiff-topology")
    subs = parser.add_subparsers()
    add_topology_subparser(subs)
    args = parser.parse_args()
    if hasattr(args, "func"):
        sys.exit(args.func(args))
    else:
        parser.print_help()
