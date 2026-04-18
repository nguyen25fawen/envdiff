"""Command-line interface for envdiff."""
import argparse
import sys
from pathlib import Path

from envdiff.comparator import compare_envs
from envdiff.formatter import format_diff
from envdiff.parser import parse_env_file


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="envdiff",
        description="Compare .env files across environments and flag missing or mismatched keys.",
    )
    parser.add_argument("file1", type=Path, help="First .env file")
    parser.add_argument("file2", type=Path, help="Second .env file")
    parser.add_argument(
        "--check-values",
        action="store_true",
        default=False,
        help="Also report keys whose values differ between files.",
    )
    parser.add_argument(
        "--show-values",
        action="store_true",
        default=False,
        help="Show actual values in output (default: mask them).",
    )
    parser.add_argument(
        "--no-color",
        action="store_true",
        default=False,
        help="Disable colored output.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    for path in (args.file1, args.file2):
        if not path.exists():
            print(f"envdiff: error: file not found: {path}", file=sys.stderr)
            return 2

    env1 = parse_env_file(args.file1)
    env2 = parse_env_file(args.file2)

    result = compare_envs(
        env1,
        env2,
        file1_name=str(args.file1),
        file2_name=str(args.file2),
        check_values=args.check_values,
    )

    output = format_diff(
        result,
        show_values=args.show_values,
        use_color=not args.no_color,
    )
    print(output)
    return 1 if result.has_differences() else 0


if __name__ == "__main__":
    sys.exit(main())
