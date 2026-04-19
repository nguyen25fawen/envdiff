"""Group env keys by prefix (e.g. DB_, AWS_, APP_) for structured reporting."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class GroupedKeys:
    groups: Dict[str, List[str]] = field(default_factory=dict)
    ungrouped: List[str] = field(default_factory=list)


def _prefix(key: str, sep: str = "_") -> str | None:
    """Return the prefix of a key if it contains sep, else None."""
    if sep in key:
        return key.split(sep, 1)[0]
    return None


def group_keys(keys: List[str], sep: str = "_") -> GroupedKeys:
    """Group a list of env keys by their prefix."""
    groups: Dict[str, List[str]] = {}
    ungrouped: List[str] = []
    for key in sorted(keys):
        p = _prefix(key, sep)
        if p:
            groups.setdefault(p, []).append(key)
        else:
            ungrouped.append(key)
    return GroupedKeys(groups=groups, ungrouped=ungrouped)


def format_groups(grouped: GroupedKeys) -> str:
    """Return a human-readable string of grouped keys."""
    lines: List[str] = []
    for prefix, keys in sorted(grouped.groups.items()):
        lines.append(f"[{prefix}]")
        for k in keys:
            lines.append(f"  {k}")
    if grouped.ungrouped:
        lines.append("[ungrouped]")
        for k in grouped.ungrouped:
            lines.append(f"  {k}")
    return "\n".join(lines)
