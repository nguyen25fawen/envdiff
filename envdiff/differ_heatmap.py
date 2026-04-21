"""Heatmap: rank keys by how frequently they differ across many env pairs."""
from __future__ import annotations

from dataclasses import dataclass, field
from collections import defaultdict
from typing import Iterable

from envdiff.differ import EnvDiff


@dataclass
class HeatmapEntry:
    key: str
    miss_count: int = 0
    mismatch_count: int = 0

    @property
    def total(self) -> int:
        return self.miss_count + self.mismatch_count

    @property
    def heat(self) -> str:
        if self.total >= 5:
            return "hot"
        if self.total >= 2:
            return "warm"
        return "cool"


@dataclass
class HeatmapResult:
    entries: list[HeatmapEntry] = field(default_factory=list)
    total_pairs: int = 0

    def is_empty(self) -> bool:
        return not self.entries

    def hottest(self, n: int = 10) -> list[HeatmapEntry]:
        return sorted(self.entries, key=lambda e: e.total, reverse=True)[:n]


def build_heatmap(diffs: Iterable[EnvDiff]) -> HeatmapResult:
    """Aggregate diff results into a key-frequency heatmap."""
    miss: dict[str, int] = defaultdict(int)
    mismatch: dict[str, int] = defaultdict(int)
    total = 0

    for diff in diffs:
        total += 1
        for key in diff.missing_in_target:
            miss[key] += 1
        for key in diff.missing_in_base:
            miss[key] += 1
        for key in diff.mismatched:
            mismatch[key] += 1

    all_keys = set(miss) | set(mismatch)
    entries = [
        HeatmapEntry(key=k, miss_count=miss[k], mismatch_count=mismatch[k])
        for k in sorted(all_keys)
    ]
    return HeatmapResult(entries=entries, total_pairs=total)
