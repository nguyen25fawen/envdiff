"""Format filtered diff results with a filter-context header."""
from __future__ import annotations

from typing import List, Optional

from envdiff.differ import EnvDiff
from envdiff.formatter import _colored, format_diff
from envdiff.comparator import DiffResult


def _to_diff_result(diff: EnvDiff, check_values: bool = True) -> DiffResult:
    """Convert EnvDiff to DiffResult for use with existing formatter."""
    return DiffResult(
        missing_in_second=dict(diff.missing_in_target),
        missing_in_first=dict(diff.missing_in_base),
        mismatched=dict(diff.mismatched) if check_values else {},
    )


def format_filtered_diff(
    diff: EnvDiff,
    target_label: str,
    patterns: Optional[List[str]] = None,
    severity: Optional[str] = None,
    check_values: bool = True,
    mask_values: bool = True,
) -> str:
    """Render a filtered diff with an optional filter context header."""
    lines: List[str] = []

    if patterns or severity:
        parts: List[str] = []
        if patterns:
            parts.append("keys=" + ",".join(patterns))
        if severity:
            parts.append("severity=" + severity)
        header = _colored("cyan", f"[filter: {' '.join(parts)}]")
        lines.append(header)

    result = _to_diff_result(diff, check_values=check_values)
    lines.append(
        format_diff(
            result,
            label_first="base",
            label_second=target_label,
            mask_values=mask_values,
        )
    )
    return "\n".join(lines)


def format_filter_summary(total_before: int, total_after: int) -> str:
    """Show how many issues remain after filtering."""
    removed = total_before - total_after
    msg = f"Showing {total_after} of {total_before} issues"
    if removed:
        msg += f" ({removed} hidden by filter)"
    return _colored("cyan", msg)
