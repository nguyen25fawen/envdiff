"""Spotlight: highlight keys that appear in only one file and have high-risk patterns."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List

from envdiff.redactor import is_sensitive

_RISK_PATTERNS: List[re.Pattern] = [
    re.compile(r"(password|passwd|secret|token|key|auth|cred)", re.I),
    re.compile(r"(private|cert|pem|pfx|p12)", re.I),
    re.compile(r"(dsn|database_url|db_url|mongo|redis|amqp)", re.I),
]


def _risk_score(key: str, value: str) -> int:
    """Return 0-3 risk score based on key/value patterns."""
    score = 0
    if is_sensitive(key):
        score += 2
    for pattern in _RISK_PATTERNS:
        if pattern.search(key):
            score += 1
            break
    if value and len(value) >= 32:
        score += 1
    return min(score, 3)


@dataclass
class SpotlightEntry:
    key: str
    value: str
    source_file: str
    risk_score: int

    @property
    def risk_label(self) -> str:
        return ["", "LOW", "MEDIUM", "HIGH"][self.risk_score]


@dataclass
class SpotlightResult:
    entries: List[SpotlightEntry] = field(default_factory=list)
    file_count: int = 0

    def is_empty(self) -> bool:
        return len(self.entries) == 0

    def by_risk(self, label: str) -> List[SpotlightEntry]:
        return [e for e in self.entries if e.risk_label == label]

    def high_risk(self) -> List[SpotlightEntry]:
        return self.by_risk("HIGH")


def build_spotlight(
    envs: Dict[str, Dict[str, str]],
    min_risk: int = 1,
) -> SpotlightResult:
    """Find keys exclusive to a single file and score their risk."""
    all_keys: Dict[str, List[str]] = {}
    for path, env in envs.items():
        for key in env:
            all_keys.setdefault(key, []).append(path)

    entries: List[SpotlightEntry] = []
    for key, sources in sorted(all_keys.items()):
        if len(sources) != 1:
            continue
        source = sources[0]
        value = envs[source].get(key, "")
        score = _risk_score(key, value)
        if score >= min_risk:
            entries.append(SpotlightEntry(key=key, value=value, source_file=source, risk_score=score))

    entries.sort(key=lambda e: (-e.risk_score, e.key))
    return SpotlightResult(entries=entries, file_count=len(envs))
