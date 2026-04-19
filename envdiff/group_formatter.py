"""Rich-style formatter for grouped env key output."""
from __future__ import annotations
from typing import Dict, List
from envdiff.grouper import GroupedKeys

TRY_COLOR = True
try:
    from colorama import Fore, Style
except ImportError:
    TRY_COLOR = False


def _c(text: str, color: str) -> str:
    if not TRY_COLOR:
        return text
    return f"{color}{text}{Style.RESET_ALL}"


def format_group_report(grouped: GroupedKeys, show_counts: bool = True) -> str:
    """Return a formatted report of grouped keys with optional counts."""
    lines: List[str] = []
    total = sum(len(v) for v in grouped.groups.values()) + len(grouped.ungrouped)
    lines.append(_c(f"Env Key Groups  ({total} keys total)", Fore.CYAN if TRY_COLOR else ""))
    lines.append("-" * 36)

    for prefix, keys in sorted(grouped.groups.items()):
        header = f"[{prefix}]"
        if show_counts:
            header += f"  ({len(keys)} keys)"
        lines.append(_c(header, Fore.YELLOW if TRY_COLOR else ""))
        for k in keys:
            lines.append(f"  {k}")

    if grouped.ungrouped:
        header = "[ungrouped]"
        if show_counts:
            header += f"  ({len(grouped.ungrouped)} keys)"
        lines.append(_c(header, Fore.WHITE if TRY_COLOR else ""))
        for k in sorted(grouped.ungrouped):
            lines.append(f"  {k}")

    if total == 0:
        return _c("No keys to group.", Fore.GREEN if TRY_COLOR else "")

    return "\n".join(lines)
