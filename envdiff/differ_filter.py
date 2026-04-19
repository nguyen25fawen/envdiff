"""Filter and slice MultiDiff results by key patterns or severity."""
from __future__ import annotations

import fnmatch
from typing import List, Optional

from envdiff.differ import EnvDiff, MultiDiff


def filter_by_keys(diff: EnvDiff, patterns: List[str]) -> EnvDiff:
    """Return a new EnvDiff keeping only keys that match any glob pattern."""
    def _match(key: str) -> bool:
        return any(fnmatch.fnmatch(key, p) for p in patterns)

    return EnvDiff(
        missing_in_target={k: v for k, v in diff.missing_in_target.items() if _match(k)},
        missing_in_base={k: v for k, v in diff.missing_in_base.items() if _match(k)},
        mismatched={k: v for k, v in diff.mismatched.items() if _match(k)},
    )


def filter_multi_by_keys(multi: MultiDiff, patterns: List[str]) -> MultiDiff:
    """Apply key filtering to every target in a MultiDiff."""
    return MultiDiff(
        base=multi.base,
        diffs={target: filter_by_keys(d, patterns) for target, d in multi.diffs.items()},
    )


def keep_only_missing(diff: EnvDiff) -> EnvDiff:
    """Strip mismatched entries, keeping only missing-key findings."""
    return EnvDiff(
        missing_in_target=dict(diff.missing_in_target),
        missing_in_base=dict(diff.missing_in_base),
        mismatched={},
    )


def keep_only_mismatched(diff: EnvDiff) -> EnvDiff:
    """Strip missing-key entries, keeping only value mismatches."""
    return EnvDiff(
        missing_in_target={},
        missing_in_base={},
        mismatched=dict(diff.mismatched),
    )


def severity_filter(diff: EnvDiff, level: str) -> EnvDiff:
    """Filter by severity level: 'missing' | 'mismatch' | 'all'."""
    if level == "missing":
        return keep_only_missing(diff)
    if level == "mismatch":
        return keep_only_mismatched(diff)
    return diff
