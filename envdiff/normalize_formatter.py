"""Rich terminal formatter for normalization results."""
from __future__ import annotations

import sys
from typing import List

from envdiff.normalizer import NormalizeResult

_RESET = "\033[0m"
_CYAN = "\033[36m"
_GREEN = "\033[32m"
_YELLOW = "\033[33m"


def _c(color: str, text: str) -> str:
    if not sys.stdout.isatty():
        return text
    return f"{color}{text}{_RESET}"


def format_normalize_rich(result: NormalizeResult, label: str = "") -> str:
    header = _c(_CYAN, f"Normalize: {label}") if label else _c(_CYAN, "Normalize")
    if not result.changes:
        return f"{header}\n  {_c(_GREEN, '✔ No changes needed.')}"
    lines: List[str] = [header]
    for change in result.changes:
        lines.append(f"  {_c(_YELLOW, '~')} {change}")
    lines.append(f"  {len(result.changes)} change(s) applied.")
    return "\n".join(lines)


def format_normalize_summary(results: List[NormalizeResult], labels: List[str]) -> str:
    total_changes = sum(len(r.changes) for r in results)
    if total_changes == 0:
        return _c(_GREEN, "All files already normalized.")
    parts: List[str] = []
    for result, label in zip(results, labels):
        if result.changes:
            parts.append(format_normalize_rich(result, label=label))
    parts.append(_c(_YELLOW, f"Total normalization changes: {total_changes}"))
    return "\n".join(parts)
