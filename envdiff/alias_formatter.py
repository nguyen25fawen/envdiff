"""alias_formatter.py – human-readable output for AliasResult."""
from __future__ import annotations

from typing import List

from .aliaser import AliasResult


def _c(text: str, code: str) -> str:
    return f"\033[{code}m{text}\033[0m"


def format_alias_result(result: AliasResult, *, color: bool = True) -> str:
    lines: List[str] = []

    if not result.renamed and not result.already_present and not result.unknown:
        msg = "No aliases applied – nothing to rename."
        return _c(msg, "32") if color else msg

    if result.renamed:
        header = "Renamed keys:"
        lines.append(_c(header, "36") if color else header)
        for old, new in sorted(result.renamed):
            arrow = f"  {old}  →  {new}"
            lines.append(_c(arrow, "32") if color else arrow)

    if result.already_present:
        header = "Skipped (new key already present):"
        lines.append(_c(header, "33") if color else header)
        for key in sorted(result.already_present):
            lines.append(f"  {key}")

    if result.unknown:
        header = "Not found (old key missing):"
        lines.append(_c(header, "31") if color else header)
        for key in sorted(result.unknown):
            lines.append(f"  {key}")

    return "\n".join(lines)


def format_alias_summary(result: AliasResult, *, color: bool = True) -> str:
    parts = [
        f"{len(result.renamed)} renamed",
        f"{len(result.already_present)} skipped",
        f"{len(result.unknown)} not found",
    ]
    summary = "Alias summary: " + ", ".join(parts) + "."
    return _c(summary, "36") if color else summary
