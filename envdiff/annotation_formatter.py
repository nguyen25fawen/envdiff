"""Format annotation summaries for display."""
from __future__ import annotations

from typing import List

from envdiff.comparator import DiffResult

try:
    from colorama import Fore, Style
    _USE_COLOR = True
except ImportError:
    _USE_COLOR = False


def _c(text: str, color: str) -> str:
    if not _USE_COLOR:
        return text
    return f"{color}{text}{Style.RESET_ALL}"


def format_annotation_summary(diff: DiffResult, path: str) -> str:
    """Return a human-readable summary of what would be annotated in *path*."""
    lines: List[str] = []
    lines.append(_c(f"Annotation preview for: {path}", ""))

    if diff.missing_in_second:
        lines.append(
            _c(f"  {len(diff.missing_in_second)} key(s) missing in target:", "")
        )
        for key in sorted(diff.missing_in_second):
            lines.append(_c(f"    - {key}", ""))

    if diff.missing_in_first:
        lines.append(
            _c(f"  {len(diff.missing_in_first)} key(s) missing in base:", "")
        )
        for key in sorted(diff.missing_in_first):
            lines.append(_c(f"    + {key}", ""))

    if diff.mismatched:
        lines.append(
            _c(f"  {len(diff.mismatched)} key(s) with value mismatch:", "")
        )
        for key in sorted(diff.mismatched):
            lines.append(_c(f"    ~ {key}", ""))

    total = (
        len(diff.missing_in_second)
        + len(diff.missing_in_first)
        + len(diff.mismatched)
    )
    if total == 0:
        lines.append(_c("  No issues found — file is clean.", ""))
    else:
        lines.append(_c(f"  Total annotations: {total}", ""))

    return "\n".join(lines)
