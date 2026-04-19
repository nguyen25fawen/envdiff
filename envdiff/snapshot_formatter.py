"""Format snapshot drift reports for terminal output."""
from __future__ import annotations

from typing import Any

TRY_COLOR = True
try:
    from colorama import Fore, Style
except ImportError:
    TRY_COLOR = False


def _c(text: str, color: str) -> str:
    if not TRY_COLOR:
        return text
    return f"{color}{text}{Style.RESET_ALL}"  # type: ignore[union-attr]


def format_drift(report: dict[str, Any], show_values: bool = False) -> str:
    lines: list[str] = []
    old = report.get("old_label", "old")
    new = report.get("new_label", "new")
    lines.append(f"Snapshot drift: {old}  →  {new}")
    lines.append("")

    if not report.get("drift_detected"):
        lines.append(_c("  ✔ No drift detected.", Fore.GREEN if TRY_COLOR else ""))  # type: ignore
        return "\n".join(lines)

    for key in report.get("added", []):
        lines.append(_c(f"  + {key}  (added)", Fore.GREEN if TRY_COLOR else ""))  # type: ignore

    for key in report.get("removed", []):
        lines.append(_c(f"  - {key}  (removed)", Fore.RED if TRY_COLOR else ""))  # type: ignore

    for key in report.get("changed", []):
        lines.append(_c(f"  ~ {key}  (changed)", Fore.YELLOW if TRY_COLOR else ""))  # type: ignore

    return "\n".join(lines)


def format_snapshot_summary(snapshot: dict[str, Any]) -> str:
    lines = [
        f"Label   : {snapshot.get('label')}",
        f"Source  : {snapshot.get('source')}",
        f"Time    : {snapshot.get('timestamp')}",
        f"Hash    : {snapshot.get('hash')}",
        f"Keys    : {len(snapshot.get('keys', []))}",
    ]
    return "\n".join(lines)
