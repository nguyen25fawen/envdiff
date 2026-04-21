"""Format RuleCheckResult for terminal output."""
from __future__ import annotations

from typing import List

from envdiff.rule_checker import RuleCheckResult, RuleViolation

_RESET = "\033[0m"
_RED = "\033[31m"
_YELLOW = "\033[33m"
_GREEN = "\033[32m"
_BOLD = "\033[1m"


def _c(text: str, *codes: str) -> str:
    return "".join(codes) + text + _RESET


def _icon(severity: str) -> str:
    return "✖" if severity == "error" else "⚠"


def _color_for(severity: str) -> str:
    return _RED if severity == "error" else _YELLOW


def format_violation(v: RuleViolation) -> str:
    icon = _icon(v.severity)
    color = _color_for(v.severity)
    label = _c(f"{icon} [{v.rule_name}]", color, _BOLD)
    key = _c(v.key, _BOLD)
    return f"  {label} {key}: {v.description}"


def format_rule_result(result: RuleCheckResult, path: str = "") -> str:
    """Return a multi-line string describing all violations."""
    lines: List[str] = []
    header = _c(f"Rule check: {path}", _BOLD) if path else _c("Rule check", _BOLD)
    lines.append(header)
    if result.is_clean:
        lines.append(_c("  ✔ No violations found.", _GREEN))
        return "\n".join(lines)
    for v in sorted(result.violations, key=lambda x: (x.key, x.rule_name)):
        lines.append(format_violation(v))
    return "\n".join(lines)


def format_rule_summary(result: RuleCheckResult) -> str:
    """Return a one-line summary of the rule check result."""
    e = len(result.errors)
    w = len(result.warnings)
    if result.is_clean:
        return _c("✔ All rules passed.", _GREEN)
    parts = []
    if e:
        parts.append(_c(f"{e} error(s)", _RED, _BOLD))
    if w:
        parts.append(_c(f"{w} warning(s)", _YELLOW, _BOLD))
    return "Rule violations: " + ", ".join(parts)
