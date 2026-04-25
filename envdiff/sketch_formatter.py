"""Formatter for SketchResult output."""
from __future__ import annotations

from typing import List

from envdiff.differ_sketch import SketchResult


def _c(text: str, code: str) -> str:
    return f"\033[{code}m{text}\033[0m"


def _sim_color(sim: float) -> str:
    if sim >= 0.9:
        return "32"  # green
    if sim >= 0.6:
        return "33"  # yellow
    return "31"  # red


def format_sketch_rich(result: SketchResult) -> str:
    if result.is_empty():
        return _c("No env files to sketch.", "33")

    lines: List[str] = []
    lines.append(_c("=== Key-Set Sketch Similarity ===", "1;36"))
    lines.append("")

    paths = [e.path for e in result.entries]
    col_w = max((len(p) for p in paths), default=10)
    header = " " * (col_w + 2) + "  ".join(f"{p:<{col_w}}" for p in paths)
    lines.append(_c(header, "2"))

    for a_path in paths:
        row_parts = [f"{a_path:<{col_w}}"]
        for b_path in paths:
            sim = result.similarity_matrix.get(a_path, {}).get(b_path, 0.0)
            label = f"{sim:.2f}"
            colored = _c(f"{label:<{col_w}}", _sim_color(sim))
            row_parts.append(colored)
        lines.append("  ".join(row_parts))

    lines.append("")
    lines.append(_c(f"Files analysed: {len(result.entries)}", "2"))
    return "\n".join(lines)


def format_sketch_summary(result: SketchResult) -> str:
    if result.is_empty():
        return "sketch: no files"
    count = len(result.entries)
    paths = [e.path for e in result.entries]
    if count < 2:
        return f"sketch: 1 file ({paths[0]}), no pairs to compare"
    pairs: List[str] = []
    for i, a in enumerate(paths):
        for b in paths[i + 1 :]:
            sim = result.similarity_matrix[a][b]
            pairs.append(f"{a}<>{b}={sim:.2f}")
    return f"sketch: {count} files | " + ", ".join(pairs)
