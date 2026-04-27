"""Whitelist-based diff filter: only report issues for keys matching allowed patterns."""
from __future__ import annotations

import fnmatch
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

from envdiff.comparator import DiffResult


@dataclass
class WhitelistResult:
    pair_label: str
    allowed_patterns: List[str]
    missing_in_second: List[str] = field(default_factory=list)
    missing_in_first: List[str] = field(default_factory=list)
    mismatched: List[str] = field(default_factory=list)

    def is_empty(self) -> bool:
        return not (self.missing_in_second or self.missing_in_first or self.mismatched)

    def by_kind(self, kind: str) -> List[str]:
        return {
            "missing_in_second": self.missing_in_second,
            "missing_in_first": self.missing_in_first,
            "mismatched": self.mismatched,
        }.get(kind, [])


def load_whitelist(path: Path) -> List[str]:
    """Load key patterns from a whitelist file, one pattern per line."""
    patterns: List[str] = []
    for raw in path.read_text().splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        patterns.append(line)
    return patterns


def _matches_any(key: str, patterns: List[str]) -> bool:
    return any(fnmatch.fnmatch(key, p) for p in patterns)


def apply_whitelist(
    diff: DiffResult,
    patterns: List[str],
    pair_label: str = "",
) -> WhitelistResult:
    """Filter a DiffResult to only include keys that match whitelist patterns."""
    result = WhitelistResult(pair_label=pair_label, allowed_patterns=list(patterns))

    for key in diff.missing_in_second:
        if _matches_any(key, patterns):
            result.missing_in_second.append(key)

    for key in diff.missing_in_first:
        if _matches_any(key, patterns):
            result.missing_in_first.append(key)

    for key in diff.mismatched:
        if _matches_any(key, patterns):
            result.mismatched.append(key)

    result.missing_in_second.sort()
    result.missing_in_first.sort()
    result.mismatched.sort()
    return result
