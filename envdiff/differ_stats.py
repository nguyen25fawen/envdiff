"""Statistics aggregation over multiple EnvDiff results."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Sequence
from envdiff.differ import EnvDiff


@dataclass
class DiffStats:
    total_pairs: int = 0
    total_missing_in_target: int = 0
    total_missing_in_base: int = 0
    total_mismatched: int = 0
    keys_always_missing: list[str] = field(default_factory=list)
    keys_always_mismatched: list[str] = field(default_factory=list)

    @property
    def total_issues(self) -> int:
        return self.total_missing_in_target + self.total_missing_in_base + self.total_mismatched

    @property
    def clean_pairs(self) -> int:
        return self.total_pairs - sum(
            1 for _ in range(self.total_pairs)
            if self.total_issues > 0
        )


def compute_stats(diffs: Sequence[EnvDiff]) -> DiffStats:
    """Aggregate statistics from a list of EnvDiff results."""
    if not diffs:
        return DiffStats()

    missing_target_counts: dict[str, int] = {}
    mismatch_counts: dict[str, int] = {}
    total_missing_in_target = 0
    total_missing_in_base = 0
    total_mismatched = 0

    for d in diffs:
        total_missing_in_target += len(d.missing_in_target)
        total_missing_in_base += len(d.missing_in_base)
        total_mismatched += len(d.mismatched)
        for k in d.missing_in_target:
            missing_target_counts[k] = missing_target_counts.get(k, 0) + 1
        for k in d.mismatched:
            mismatch_counts[k] = mismatch_counts.get(k, 0) + 1

    n = len(diffs)
    always_missing = sorted(k for k, v in missing_target_counts.items() if v == n)
    always_mismatched = sorted(k for k, v in mismatch_counts.items() if v == n)

    return DiffStats(
        total_pairs=n,
        total_missing_in_target=total_missing_in_target,
        total_missing_in_base=total_missing_in_base,
        total_mismatched=total_mismatched,
        keys_always_missing=always_missing,
        keys_always_mismatched=always_mismatched,
    )
