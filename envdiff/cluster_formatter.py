"""Formatter for ClusterResult."""
from __future__ import annotations

from typing import List

from envdiff.differ_cluster import ClusterResult


def _c(text: str, code: str) -> str:
    return f"\033[{code}m{text}\033[0m"


def format_cluster_rich(
    result: ClusterResult,
    threshold: float = 0.5,
    show_similarity: bool = False,
) -> str:
    if result.is_empty():
        return _c("No files to cluster.", "33")

    lines: List[str] = [
        _c(f"Cluster Report  (threshold={threshold:.0%})", "1;36"),
        "",
    ]

    for idx, group in enumerate(result.groups, 1):
        label = _c(f"Group {idx}", "1;34")
        lines.append(f"  {label} ({len(group)} file{'s' if len(group) != 1 else ''})")
        for path in group:
            lines.append(f"    {_c(path, '32')}")

        if show_similarity and len(group) > 1:
            entry_map = {e.path: e for e in result.entries}
            for i, p1 in enumerate(group):
                for p2 in group[i + 1 :]:
                    sim = entry_map[p1].shared_with.get(p2, 0.0)
                    lines.append(
                        f"      {_c(p1, '33')} <-> {_c(p2, '33')}: {sim:.0%} shared"
                    )
        lines.append("")

    return "\n".join(lines).rstrip()


def format_cluster_summary(result: ClusterResult) -> str:
    if result.is_empty():
        return "No files clustered."
    total = len(result.entries)
    groups = len(result.groups)
    singletons = sum(1 for g in result.groups if len(g) == 1)
    return (
        f"{total} file(s) across {groups} cluster(s); "
        f"{singletons} singleton(s)."
    )
