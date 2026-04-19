"""Format interpolation results for terminal output."""
from __future__ import annotations

from typing import List

from .interpolator import InterpolationResult


def _c(text: str, code: str) -> str:
    return f"\033[{code}m{text}\033[0m"


def format_interpolation_result(result: InterpolationResult, *, show_resolved: bool = False) -> str:
    lines: List[str] = []

    if result.unresolved:
        lines.append(_c("Unresolved interpolations:", "1;31"))
        for key, missing in sorted(result.unresolved.items()):
            refs = ", ".join(f"${r}" for r in missing)
            lines.append(f"  {_c(key, '33')} references missing: {_c(refs, '31')}")
    else:
        lines.append(_c("All interpolations resolved.", "32"))

    if show_resolved and result.references:
        lines.append("")
        lines.append(_c("Resolved references:", "1;34"))
        for key in sorted(result.references):
            val = result.resolved.get(key, "")
            lines.append(f"  {_c(key, '36')} -> {val}")

    return "\n".join(lines)


def format_interpolation_summary(result: InterpolationResult) -> str:
    total = len(result.references)
    bad = len(result.unresolved)
    ok = total - bad
    parts = [
        _c(f"{total} interpolated key(s)", "1"),
        _c(f"{ok} resolved", "32"),
        _c(f"{bad} unresolved", "31" if bad else "32"),
    ]
    return "  ".join(parts)
