"""Format AuditResult for terminal output."""
from __future__ import annotations
from typing import List
from envdiff.auditor import AuditResult

RED = "\033[31m"
YELLOW = "\033[33m"
GREEN = "\033[32m"
BOLD = "\033[1m"
RESET = "\033[0m"


def _c(color: str, text: str, no_color: bool = False) -> str:
    return text if no_color else f"{color}{text}{RESET}"


def _icon(severity: str) -> str:
    return "✖" if severity == "error" else "⚠"


def format_audit_result(result: AuditResult, no_color: bool = False) -> str:
    lines: List[str] = []
    header = f"{BOLD}{result.path}{RESET}" if not no_color else result.path
    lines.append(header)
    if result.is_clean():
        lines.append(_c(GREEN, "  ✔ No audit issues found.", no_color))
        return "\n".join(lines)
    for issue in result.issues:
        color = RED if issue.severity == "error" else YELLOW
        icon = _icon(issue.severity)
        lines.append(_c(color, f"  {icon} [{issue.severity.upper()}] {issue.key}: {issue.message}", no_color))
    return "\n".join(lines)


def format_audit_summary(results: List[AuditResult], no_color: bool = False) -> str:
    total_errors = sum(len(r.errors()) for r in results)
    total_warnings = sum(len(r.warnings()) for r in results)
    lines = []
    lines.append("")
    if total_errors == 0 and total_warnings == 0:
        lines.append(_c(GREEN, "Audit passed: no issues detected.", no_color))
    else:
        parts = []
        if total_errors:
            parts.append(_c(RED, f"{total_errors} error(s)", no_color))
        if total_warnings:
            parts.append(_c(YELLOW, f"{total_warnings} warning(s)", no_color))
        lines.append("Audit summary: " + ", ".join(parts))
    return "\n".join(lines)
