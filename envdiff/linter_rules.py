"""Built-in lint rule definitions and registry for envdiff linter."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Dict, List


@dataclass(frozen=True)
class LintRule:
    """A single named lint rule with a severity and check function."""

    name: str
    severity: str  # "error" or "warning"
    description: str
    check: Callable[[str, str], bool] = field(compare=False, repr=False)


def _is_empty_value(key: str, value: str) -> bool:
    return value.strip() == ""


def _is_whitespace_key(key: str, value: str) -> bool:
    return key != key.strip()


def _is_lowercase_key(key: str, value: str) -> bool:
    return key != key.upper() and key.upper() == key.upper()


def _has_spaces_in_key(key: str, value: str) -> bool:
    return " " in key


def _value_has_unquoted_spaces(key: str, value: str) -> bool:
    if value.startswith(("'", '"')):
        return False
    return " " in value


def _key_starts_with_digit(key: str, value: str) -> bool:
    return bool(key) and key[0].isdigit()


DEFAULT_RULES: List[LintRule] = [
    LintRule(
        name="empty-value",
        severity="warning",
        description="Key has an empty value.",
        check=_is_empty_value,
    ),
    LintRule(
        name="whitespace-in-key",
        severity="error",
        description="Key contains surrounding whitespace.",
        check=_is_whitespace_key,
    ),
    LintRule(
        name="spaces-in-key",
        severity="error",
        description="Key contains spaces.",
        check=_has_spaces_in_key,
    ),
    LintRule(
        name="unquoted-spaces-in-value",
        severity="warning",
        description="Value contains spaces but is not quoted.",
        check=_value_has_unquoted_spaces,
    ),
    LintRule(
        name="key-starts-with-digit",
        severity="error",
        description="Key starts with a digit, which is invalid in most shells.",
        check=_key_starts_with_digit,
    ),
]


def rule_by_name(name: str) -> LintRule | None:
    """Return a rule by its name, or None if not found."""
    return next((r for r in DEFAULT_RULES if r.name == name), None)


def rules_by_severity(severity: str) -> List[LintRule]:
    """Return all rules matching the given severity."""
    return [r for r in DEFAULT_RULES if r.severity == severity]
