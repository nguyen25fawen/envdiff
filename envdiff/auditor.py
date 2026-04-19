"""Audit env files for security and compliance issues."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List
from envdiff.parser import parse_env_file
from envdiff.redactor import is_sensitive


@dataclass
class AuditIssue:
    key: str
    message: str
    severity: str  # "error" | "warning"


@dataclass
class AuditResult:
    path: str
    issues: List[AuditIssue] = field(default_factory=list)

    def is_clean(self) -> bool:
        return len(self.issues) == 0

    def errors(self) -> List[AuditIssue]:
        return [i for i in self.issues if i.severity == "error"]

    def warnings(self) -> List[AuditIssue]:
        return [i for i in self.issues if i.severity == "warning"]


def _check_plaintext_sensitive(key: str, value: str) -> AuditIssue | None:
    if is_sensitive(key) and value and value not in ("", "REDACTED"):
        return AuditIssue(key=key, message="Sensitive key has plaintext value", severity="error")
    return None


def _check_placeholder(key: str, value: str) -> AuditIssue | None:
    placeholders = {"changeme", "todo", "fixme", "placeholder", "example", "your_value"}
    if value.lower() in placeholders:
        return AuditIssue(key=key, message=f"Value looks like a placeholder: '{value}'", severity="warning")
    return None


def _check_http_url(key: str, value: str) -> AuditIssue | None:
    if value.startswith("http://") and is_sensitive(key):
        return AuditIssue(key=key, message="Sensitive key uses insecure http:// URL", severity="warning")
    return None


def audit_env(path: str) -> AuditResult:
    env: Dict[str, str] = parse_env_file(path)
    result = AuditResult(path=path)
    for key, value in env.items():
        for check in (_check_plaintext_sensitive, _check_placeholder, _check_http_url):
            issue = check(key, value)
            if issue:
                result.issues.append(issue)
    return result
