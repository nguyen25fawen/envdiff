"""Apply lint rules to a parsed env dict and collect violations."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from envdiff.linter_rules import DEFAULT_RULES, LintRule


@dataclass
class RuleViolation:
    """A single rule violation for a specific key."""

    rule_name: str
    severity: str
    key: str
    description: str

    def __str__(self) -> str:
        return f"[{self.severity.upper()}] {self.key}: {self.description} (rule: {self.rule_name})"


@dataclass
class RuleCheckResult:
    """Aggregated result of running all rules over an env dict."""

    violations: List[RuleViolation] = field(default_factory=list)

    @property
    def is_clean(self) -> bool:
        return len(self.violations) == 0

    @property
    def errors(self) -> List[RuleViolation]:
        return [v for v in self.violations if v.severity == "error"]

    @property
    def warnings(self) -> List[RuleViolation]:
        return [v for v in self.violations if v.severity == "warning"]


def check_rules(
    env: Dict[str, str],
    rules: Optional[List[LintRule]] = None,
    skip: Optional[List[str]] = None,
) -> RuleCheckResult:
    """Run lint rules against an env dict.

    Args:
        env: Parsed key/value pairs.
        rules: Rules to apply; defaults to DEFAULT_RULES.
        skip: Rule names to skip.

    Returns:
        RuleCheckResult with all violations found.
    """
    if rules is None:
        rules = DEFAULT_RULES
    skip_set = set(skip or [])
    result = RuleCheckResult()
    for rule in rules:
        if rule.name in skip_set:
            continue
        for key, value in env.items():
            if rule.check(key, value):
                result.violations.append(
                    RuleViolation(
                        rule_name=rule.name,
                        severity=rule.severity,
                        key=key,
                        description=rule.description,
                    )
                )
    return result


def check_rules_from_file(path: str, skip: Optional[List[str]] = None) -> RuleCheckResult:
    """Parse an env file and run all default lint rules against it."""
    from envdiff.parser import parse_env_file

    env = parse_env_file(path)
    return check_rules(env, skip=skip)
