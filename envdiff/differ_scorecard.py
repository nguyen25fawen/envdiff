"""Scorecard: aggregate health metrics across multiple env diff pairs."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from envdiff.differ import EnvDiff


@dataclass
class ScorecardEntry:
    label: str
    total_keys: int
    missing_in_target: int
    missing_in_base: int
    mismatched: int

    @property
    def total_issues(self) -> int:
        return self.missing_in_target + self.missing_in_base + self.mismatched

    @property
    def health_pct(self) -> float:
        if self.total_keys == 0:
            return 100.0
        clean = self.total_keys - self.total_issues
        return round(max(clean, 0) / self.total_keys * 100, 1)


@dataclass
class ScorecardResult:
    entries: List[ScorecardEntry] = field(default_factory=list)

    @property
    def is_empty(self) -> bool:
        return len(self.entries) == 0

    @property
    def overall_health(self) -> float:
        if not self.entries:
            return 100.0
        return round(sum(e.health_pct for e in self.entries) / len(self.entries), 1)

    @property
    def any_issues(self) -> bool:
        return any(e.total_issues > 0 for e in self.entries)


def _all_keys(diff: EnvDiff) -> int:
    keys = set(diff.base.keys()) | set(diff.target.keys())
    return len(keys)


def build_scorecard(
    diffs: List[EnvDiff],
    labels: List[str] | None = None,
) -> ScorecardResult:
    """Build a ScorecardResult from a list of EnvDiff objects."""
    result = ScorecardResult()
    for i, diff in enumerate(diffs):
        label = (labels[i] if labels and i < len(labels) else f"pair-{i + 1}")
        entry = ScorecardEntry(
            label=label,
            total_keys=_all_keys(diff),
            missing_in_target=len(diff.missing_in_target),
            missing_in_base=len(diff.missing_in_base),
            mismatched=len(diff.mismatched),
        )
        result.entries.append(entry)
    return result
