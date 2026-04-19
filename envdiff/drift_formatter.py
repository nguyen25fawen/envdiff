"""Format DriftReport objects for terminal output."""
from __future__ import annotations

from typing import List

from envdiff.drifter import DriftReport


def _c(text: str, code: str) -> str:
    return f"\033[{code}m{text}\033[0m"


def _icon(kind: str) -> str:
    return {"added": _c("+", "32"), "removed": _c("-", "31"), "changed": _c("~", "33")}.get(kind, " ")


def format_drift_report(report: DriftReport, show_values: bool = False) -> str:
    lines: List[str] = []
    lines.append(_c(f"Drift: {report.base} → {report.target}", "1"))

    if not report.has_drift():
        lines.append(_c("  No drift detected.", "32"))
        return "\n".join(lines)

    for entry in report.entries:
        icon = _icon(entry.kind)
        label = _c(entry.key, "1")
        if show_values:
            bv = entry.base_value if entry.base_value is not None else _c("(absent)", "2")
            tv = entry.target_value if entry.target_value is not None else _c("(absent)", "2")
            lines.append(f"  {icon} {label}  {_c(bv, '2')} → {_c(tv, '2')}")
        else:
            lines.append(f"  {icon} {label}  [{entry.kind}]")

    return "\n".join(lines)


def format_drift_summary(reports: List[DriftReport]) -> str:
    total = sum(len(r.entries) for r in reports)
    drifted = sum(1 for r in reports if r.has_drift())
    lines = [_c("Drift Summary", "1")]
    for r in reports:
        status = _c(str(len(r.entries)) + " issues", "31") if r.has_drift() else _c("clean", "32")
        lines.append(f"  {r.target}: {status}")
    lines.append(f"  {drifted}/{len(reports)} targets drifted, {total} total issues.")
    return "\n".join(lines)
