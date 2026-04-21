"""Formatter for BaselineResult output."""
from __future__ import annotations

from typing import List

from envdiff.baseline import BaselineResult
from envdiff.formatter import format_diff


def _c(text: str, code: str) -> str:
    return f"\033[{code}m{text}\033[0m"


def format_baseline_result(
    result: BaselineResult,
    show_values: bool = False,
) -> str:
    lines: List[str] = [
        _c(f"Baseline: {result.base_path}", "1;34"),
        "",
    ]
    for target_path, diff in result.comparisons.items():
        header = _c(f"  vs {target_path}", "1;33")
        lines.append(header)
        diff_text = format_diff(diff, show_values=show_values)
        for line in diff_text.splitlines():
            lines.append(f"    {line}")
        lines.append("")
    return "\n".join(lines).rstrip()


def format_baseline_summary(result: BaselineResult) -> str:
    total = len(result.comparisons)
    issues = len(result.targets_with_issues())
    clean = len(result.clean_targets())
    lines = [
        _c("Baseline Summary", "1;34"),
        f"  Base       : {result.base_path}",
        f"  Targets    : {total}",
        f"  Clean      : {_c(str(clean), '1;32')}",
        f"  With issues: {_c(str(issues), '1;31') if issues else _c('0', '1;32')}",
    ]
    return "\n".join(lines)
