"""Watchlist: flag diffs that touch a set of high-priority keys."""
from __future__ import annotations

import fnmatch
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable

from envdiff.comparator import DiffResult


@dataclass
class WatchlistHit:
    key: str
    pattern: str
    kind: str  # "missing_in_second" | "missing_in_first" | "mismatch"


@dataclass
class WatchlistResult:
    patterns: list[str]
    hits: list[WatchlistHit] = field(default_factory=list)

    def is_empty(self) -> bool:
        return len(self.hits) == 0

    def by_kind(self, kind: str) -> list[WatchlistHit]:
        return [h for h in self.hits if h.kind == kind]


def load_watchlist(path: str | Path) -> list[str]:
    """Read patterns from a file, one per line; skip comments and blanks."""
    lines = Path(path).read_text().splitlines()
    return [
        ln.strip()
        for ln in lines
        if ln.strip() and not ln.strip().startswith("#")
    ]


def _matches_any(key: str, patterns: Iterable[str]) -> str | None:
    """Return the first matching pattern or None."""
    for pat in patterns:
        if fnmatch.fnmatch(key, pat):
            return pat
    return None


def apply_watchlist(
    diff: DiffResult,
    patterns: list[str],
) -> WatchlistResult:
    """Scan a DiffResult for keys that match any watchlist pattern."""
    result = WatchlistResult(patterns=patterns)

    for key in diff.missing_in_second:
        pat = _matches_any(key, patterns)
        if pat:
            result.hits.append(WatchlistHit(key=key, pattern=pat, kind="missing_in_second"))

    for key in diff.missing_in_first:
        pat = _matches_any(key, patterns)
        if pat:
            result.hits.append(WatchlistHit(key=key, pattern=pat, kind="missing_in_first"))

    for key in diff.mismatched:
        pat = _matches_any(key, patterns)
        if pat:
            result.hits.append(WatchlistHit(key=key, pattern=pat, kind="mismatch"))

    result.hits.sort(key=lambda h: h.key)
    return result
