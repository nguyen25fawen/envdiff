"""Format OverlapResult for terminal output."""
from __future__ import annotations

from typing import List

from envdiff.differ_overlap import OverlapResult


def _c(code: str, text: str) -> str:
    return f"\033[{code}m{text}\033[0m"


def format_overlap_rich(result: OverlapResult, show_coverage: bool = False) -> str:
    lines: List[str] = []
    lines.append(_c("1;34", f"Key Overlap Report ({len(result.files)} files)"))
    lines.append("")

    universal = sorted(result.universal_keys)
    if universal:
        lines.append(_c("1;32", f"  Universal keys ({len(universal)}):"))
        for k in universal:
            suffix = f"  [{result.coverage(k):.0%}]" if show_coverage else ""
            lines.append(f"    {_c('32', k)}{suffix}")
        lines.append("")

    partial = sorted(result.partial_keys)
    if partial:
        lines.append(_c("1;33", f"  Partial keys ({len(partial)}):"))
        for k in partial:
            count = len(result.key_presence[k])
            suffix = f"  [{result.coverage(k):.0%}]" if show_coverage else f"  ({count}/{len(result.files)} files)"
            lines.append(f"    {_c('33', k)}{suffix}")
        lines.append("")

    exclusive = result.exclusive_keys
    if exclusive:
        lines.append(_c("1;31", f"  Exclusive keys ({len(exclusive)}):"))
        for k, path in sorted(exclusive.items()):
            lines.append(f"    {_c('31', k)}  [{path}]")
        lines.append("")

    return "\n".join(lines)


def format_overlap_summary(result: OverlapResult) -> str:
    total = len(result.all_keys)
    u = len(result.universal_keys)
    p = len(result.partial_keys)
    e = len(result.exclusive_keys)
    return (
        f"Overlap: {total} total keys — "
        f"{_c('32', str(u))} universal, "
        f"{_c('33', str(p))} partial, "
        f"{_c('31', str(e))} exclusive"
    )
