"""Formatters for TopologyResult."""
from __future__ import annotations

from typing import List

from envdiff.differ_topology import TopologyResult


def _c(text: str, code: str) -> str:
    return f"\033[{code}m{text}\033[0m"


def format_topology_rich(result: TopologyResult, *, show_shared: bool = False) -> str:
    if result.is_empty():
        return _c("No files to analyse.", "33")

    lines: List[str] = [_c("Topology Analysis", "1;36"), ""]

    lines.append(_c("Nodes", "1;37"))
    for node in result.nodes:
        lines.append(f"  {_c(node.path, '36')}  ({node.key_count} keys)")

    lines.append("")
    lines.append(_c("Edges (pairwise overlap)", "1;37"))
    if not result.edges:
        lines.append("  (no pairs)")
    else:
        for edge in sorted(result.edges, key=lambda e: -e.overlap_pct):
            pct_str = f"{edge.overlap_pct:.1f}%"
            color = "32" if edge.overlap_pct >= 80 else ("33" if edge.overlap_pct >= 40 else "31")
            lines.append(
                f"  {edge.source}  <->  {edge.target}  "
                f"[{_c(pct_str, color)}  {len(edge.shared_keys)} shared]"
            )
            if show_shared and edge.shared_keys:
                for k in sorted(edge.shared_keys):
                    lines.append(f"      {_c(k, '90')}")

    return "\n".join(lines)


def format_topology_summary(result: TopologyResult) -> str:
    if result.is_empty():
        return "topology: no files"
    avg_overlap = (
        sum(e.overlap_pct for e in result.edges) / len(result.edges)
        if result.edges
        else 0.0
    )
    return (
        f"topology: {len(result.nodes)} files, "
        f"{len(result.edges)} pairs, "
        f"avg overlap {avg_overlap:.1f}%"
    )
