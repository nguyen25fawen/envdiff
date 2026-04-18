"""Format LintResult objects for terminal output."""
from __future__ import annotations

from typing import List
from envdiff.linter import LintResult, LintIssue

TRY_COLOR = True
try:
    import sys
    _COLOR = sys.stdout.isatty()
except Exception:
    _COLOR = False


def _c(text: str, code: str) -> str:
    if not _COLOR:
        return text
    return f"\033[{code}m{text}\033[0m"


def _icon(severity: str) -> str:
    if severity == "error":
        return _c("✖", "31")
    return _c("⚠", "33")


def format_lint_result(result: LintResult) -> List[str]:
    lines: List[str] = []
    header = _c(str(result.path), "1")
    if result.is_clean:
        lines.append(f"{header}: {_c('no issues found', '32')}")
        return lines

    lines.append(f"{header}: {len(result.issues)} issue(s)")
    for issue in result.issues:
        loc = _c(f"line {issue.line_number}", "2")
        icon = _icon(issue.severity)
        lines.append(f"  {icon} [{loc}] {issue.message}")
    return lines


def format_lint_summary(results: List[LintResult]) -> List[str]:
    lines: List[str] = []
    for r in results:
        lines.extend(format_lint_result(r))
    total_errors = sum(len(r.errors) for r in results)
    total_warnings = sum(len(r.warnings) for r in results)
    lines.append("")
    if total_errors == 0 and total_warnings == 0:
        lines.append(_c("All files passed linting.", "32"))
    else:
        parts = []
        if total_errors:
            parts.append(_c(f"{total_errors} error(s)", "31"))
        if total_warnings:
            parts.append(_c(f"{total_warnings} warning(s)", "33"))
        lines.append("Summary: " + ", ".join(parts))
    return lines
