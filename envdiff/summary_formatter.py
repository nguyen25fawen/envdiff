"""Format an EnvSummary for terminal output."""
from __future__ import annotations
from typing import List
from envdiff.summarizer import EnvSummary


def _c(text: str, code: str) -> str:
    return f"\033[{code}m{text}\033[0m"


def format_summary(summary: EnvSummary, *, color: bool = True) -> str:
    lines: List[str] = []

    header = f"Env Summary — {len(summary.files)} file(s), {summary.total_keys()} key(s)"
    lines.append(_c(header, "1;34") if color else header)
    lines.append("")

    universal = summary.universal_keys()
    partial = summary.partial_keys()

    if universal:
        label = _c(f"Universal keys ({len(universal)}):", "1;32") if color else f"Universal keys ({len(universal)}):"
        lines.append(label)
        for k in universal:
            stat = summary.stats[k]
            note = f"  {k}"
            if stat.unique_values > 1:
                note += _c(" [values differ]", "33") if color else " [values differ]"
            if stat.has_empty:
                note += _c(" [has empty]", "33") if color else " [has empty]"
            lines.append(note)
        lines.append("")

    if partial:
        label = _c(f"Partial keys ({len(partial)}):", "1;31") if color else f"Partial keys ({len(partial)}):"
        lines.append(label)
        for k in partial:
            stat = summary.stats[k]
            missing_str = ", ".join(stat.missing_in)
            row = f"  {k}" + (_c(f" [missing in: {missing_str}]", "31") if color else f" [missing in: {missing_str}]")
            lines.append(row)
        lines.append("")

    return "\n".join(lines)
