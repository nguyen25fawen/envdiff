"""Lint .env files for common issues like duplicate keys, empty values, and invalid lines."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import List


@dataclass
class LintIssue:
    line_number: int
    key: str | None
    message: str
    severity: str  # "error" | "warning"


@dataclass
class LintResult:
    path: Path
    issues: List[LintIssue] = field(default_factory=list)

    @property
    def is_clean(self) -> bool:
        return len(self.issues) == 0

    @property
    def errors(self) -> List[LintIssue]:
        return [i for i in self.issues if i.severity == "error"]

    @property
    def warnings(self) -> List[LintIssue]:
        return [i for i in self.issues if i.severity == "warning"]


def lint_file(path: Path) -> LintResult:
    result = LintResult(path=path)
    seen_keys: dict[str, int] = {}

    with open(path, "r", encoding="utf-8") as fh:
        for lineno, raw in enumerate(fh, start=1):
            line = raw.rstrip("\n")
            stripped = line.strip()

            if not stripped or stripped.startswith("#"):
                continue

            if "=" not in stripped:
                result.issues.append(
                    LintIssue(lineno, None, f"Invalid line (no '=' found): {line!r}", "error")
                )
                continue

            key, _, value = stripped.partition("=")
            key = key.strip()

            if not key:
                result.issues.append(
                    LintIssue(lineno, key, "Empty key name", "error")
                )
                continue

            if key in seen_keys:
                result.issues.append(
                    LintIssue(
                        lineno, key,
                        f"Duplicate key '{key}' (first seen on line {seen_keys[key]})",
                        "error",
                    )
                )
            else:
                seen_keys[key] = lineno

            if not value.strip():
                result.issues.append(
                    LintIssue(lineno, key, f"Key '{key}' has an empty value", "warning")
                )

    return result
