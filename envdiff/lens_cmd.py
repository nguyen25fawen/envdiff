"""CLI sub-command: envdiff lens — apply a named lens to a diff."""
from __future__ import annotations

import argparse
import sys

from envdiff.comparator import compare_envs
from envdiff.differ_lens import apply_lens, load_lens_rules
from envdiff.lens_formatter import format_lens_rich, format_lens_summary
from envdiff.parser import parse_env_file


def add_lens_subparser(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser(
        "lens",
        help="Focus diff output through a named lens (pattern-based key filter).",
    )
    p.add_argument("base", help="Base .env file")
    p.add_argument("target", help="Target .env file")
    p.add_argument(
        "--lens-file",
        required=True,
        metavar="FILE",
        help="Path to lens rules file",
    )
    p.add_argument(
        "--lens-name",
        required=True,
        metavar="NAME",
        help="Name of the lens to apply",
    )
    p.add_argument(
        "--check-values",
        action="store_true",
        default=False,
        help="Compare values in addition to key presence",
    )
    p.add_argument(
        "--show-values",
        action="store_true",
        default=False,
        help="Print actual values for mismatches (implies --check-values)",
    )
    p.add_argument("--summary", action="store_true", help="Print one-line summary only")
    p.set_defaults(func=_run)


def _run(args: argparse.Namespace) -> int:
    base_env = parse_env_file(args.base)
    target_env = parse_env_file(args.target)
    check_values = args.check_values or args.show_values

    diff = compare_envs(base_env, target_env, check_values=check_values)

    rules = load_lens_rules(args.lens_file)
    matched = [r for r in rules if r.name == args.lens_name]
    if not matched:
        print(f"Error: lens '{args.lens_name}' not found in {args.lens_file}", file=sys.stderr)
        return 2

    result = apply_lens(diff, matched[0])

    if args.summary:
        print(format_lens_summary(result))
    else:
        print(format_lens_rich(result, show_values=args.show_values))

    return 1 if result.matched_keys > 0 else 0


def main() -> None:
    parser = argparse.ArgumentParser(prog="envdiff-lens")
    subs = parser.add_subparsers()
    add_lens_subparser(subs)
    args = parser.parse_args()
    sys.exit(_run(args))
