"""CLI subcommand: envdiff cluster — group .env files by similarity."""
from __future__ import annotations

import argparse
import sys
from typing import List, Optional

from envdiff.differ_cluster import cluster_files
from envdiff.cluster_formatter import format_cluster_rich, format_cluster_summary


def add_cluster_subparser(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser(
        "cluster",
        help="Group .env files by key-set similarity.",
    )
    p.add_argument("files", nargs="+", metavar="FILE", help=".env files to cluster")
    p.add_argument(
        "--threshold",
        type=float,
        default=0.5,
        metavar="FLOAT",
        help="Jaccard similarity threshold (0.0–1.0, default 0.5)",
    )
    p.add_argument(
        "--show-similarity",
        action="store_true",
        default=False,
        help="Show pairwise similarity scores within each group",
    )
    p.add_argument(
        "--summary",
        action="store_true",
        default=False,
        help="Print one-line summary instead of full report",
    )
    p.set_defaults(func=_run)


def _run(args: argparse.Namespace) -> int:
    result = cluster_files(args.files, threshold=args.threshold)
    if args.summary:
        print(format_cluster_summary(result))
    else:
        print(
            format_cluster_rich(
                result,
                threshold=args.threshold,
                show_similarity=args.show_similarity,
            )
        )
    return 0


def main(argv: Optional[List[str]] = None) -> None:
    parser = argparse.ArgumentParser(
        prog="envdiff-cluster",
        description="Cluster .env files by key-set similarity.",
    )
    parser.add_argument("files", nargs="+", metavar="FILE")
    parser.add_argument("--threshold", type=float, default=0.5)
    parser.add_argument("--show-similarity", action="store_true", default=False)
    parser.add_argument("--summary", action="store_true", default=False)
    args = parser.parse_args(argv)
    sys.exit(_run(args))
