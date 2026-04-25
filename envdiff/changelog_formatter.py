"""Format a ChangelogResult for terminal output."""
from __future__ import annotations

from typing import List

from .differ_changelog import ChangelogResult


def _c(text: str, code: str) -> str:
    return f"\033[{code}m{text}\033[0m"


_ICONS = {"added": "+", "removed": "-", "changed": "~"}
_COLORS = {"added": "32", "removed": "31", "changed": "33"}


def format_changelog_rich(result: ChangelogResult, show_values: bool = False) -> str:
    lines: List[str] = []
    header = _c(
        f"Changelog  {result.base_label}  →  {result.target_label}", "1;36"
    )
    lines.append(header)
    lines.append(_c("-" * len(header.replace("\033[1;36m", "").replace("\033[0m", "")), "90"))

    if result.is_empty():
        lines.append(_c("  No changes detected.", "32"))
        return "\n".join(lines)

    for entry in result.entries:
        icon = _ICONS[entry.kind]
        color = _COLORS[entry.kind]
        label = _c(f"  [{icon}] {entry.key}", color)

        if show_values:
            if entry.kind == "added":
                label += f"  =  {entry.new_value}"
            elif entry.kind == "removed":
                label += f"  (was: {entry.old_value})"
            elif entry.kind == "changed":
                label += f"  {entry.old_value!r}  →  {entry.new_value!r}"

        lines.append(label)

    return "\n".join(lines)


def format_changelog_summary(result: ChangelogResult) -> str:
    added = len(result.by_kind("added"))
    removed = len(result.by_kind("removed"))
    changed = len(result.by_kind("changed"))
    total = added + removed + changed

    if total == 0:
        return _c("changelog: no changes", "32")

    parts = []
    if added:
        parts.append(_c(f"+{added} added", "32"))
    if removed:
        parts.append(_c(f"-{removed} removed", "31"))
    if changed:
        parts.append(_c(f"~{changed} changed", "33"))

    return "changelog: " + "  ".join(parts)
