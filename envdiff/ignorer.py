"""Key ignore list support: load and apply ignore patterns for diff filtering."""

from __future__ import annotations

import fnmatch
import re
from pathlib import Path
from typing import Iterable


def load_ignore_patterns(path: str | Path) -> list[str]:
    """Read ignore patterns from a file (one per line, # comments ignored)."""
    patterns: list[str] = []
    for line in Path(path).read_text().splitlines():
        stripped = line.strip()
        if stripped and not stripped.startswith("#"):
            patterns.append(stripped)
    return patterns


def is_ignored(key: str, patterns: Iterable[str]) -> bool:
    """Return True if *key* matches any of the given glob/regex patterns."""
    for pattern in patterns:
        if pattern.startswith("re:"):
            if re.search(pattern[3:], key):
                return True
        elif fnmatch.fnmatch(key, pattern):
            return True
    return False


def filter_keys(
    keys: Iterable[str],
    patterns: Iterable[str],
) -> list[str]:
    """Return keys that are NOT ignored by any pattern."""
    pat = list(patterns)
    return [k for k in keys if not is_ignored(k, pat)]


def apply_ignore(
    env: dict[str, str],
    patterns: Iterable[str],
) -> dict[str, str]:
    """Return a copy of *env* with ignored keys removed."""
    pat = list(patterns)
    return {k: v for k, v in env.items() if not is_ignored(k, pat)}
