"""Lens module: focus diff results on a specific subset of keys using a named lens."""
from __future__ import annotations

from dataclasses import dataclass, field
from fnmatch import fnmatch
from typing import Dict, List, Optional

from envdiff.comparator import DiffResult


@dataclass
class LensRule:
    name: str
    patterns: List[str]


@dataclass
class LensResult:
    lens: LensRule
    focused: DiffResult
    total_keys: int
    matched_keys: int


def load_lens_rules(path: str) -> List[LensRule]:
    """Load lens rules from a simple INI-like file.

    Format::
        [lens_name]
        PATTERN_*
        ANOTHER_KEY
    """
    rules: List[LensRule] = []
    current_name: Optional[str] = None
    current_patterns: List[str] = []

    with open(path) as fh:
        for raw in fh:
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            if line.startswith("[") and line.endswith("]"):
                if current_name is not None:
                    rules.append(LensRule(name=current_name, patterns=list(current_patterns)))
                current_name = line[1:-1].strip()
                current_patterns = []
            else:
                current_patterns.append(line)

    if current_name is not None:
        rules.append(LensRule(name=current_name, patterns=list(current_patterns)))

    return rules


def _matches_any(key: str, patterns: List[str]) -> bool:
    return any(fnmatch(key, p) for p in patterns)


def apply_lens(diff: DiffResult, lens: LensRule) -> LensResult:
    """Filter a DiffResult to only keys matching the lens patterns."""
    all_keys = (
        set(diff.missing_in_second)
        | set(diff.missing_in_first)
        | set(diff.mismatched)
    )
    total = len(all_keys)

    focused = DiffResult(
        missing_in_second=[k for k in diff.missing_in_second if _matches_any(k, lens.patterns)],
        missing_in_first=[k for k in diff.missing_in_first if _matches_any(k, lens.patterns)],
        mismatched={
            k: v for k, v in diff.mismatched.items() if _matches_any(k, lens.patterns)
        },
    )

    matched = (
        len(focused.missing_in_second)
        + len(focused.missing_in_first)
        + len(focused.mismatched)
    )

    return LensResult(lens=lens, focused=focused, total_keys=total, matched_keys=matched)
