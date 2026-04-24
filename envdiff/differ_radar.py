"""Radar chart data builder for multi-file env comparisons.

Produces per-file dimension scores suitable for rendering
as a radar / spider chart or a simple textual summary.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Sequence

from envdiff.differ import EnvDiff


@dataclass
class RadarAxis:
    """A single dimension (axis) of the radar chart."""
    name: str
    score: float          # 0.0 – 1.0
    raw_value: int        # absolute count driving the score


@dataclass
class RadarEntry:
    """Radar profile for one .env file."""
    path: str
    axes: List[RadarAxis] = field(default_factory=list)

    @property
    def overall(self) -> float:
        """Mean score across all axes."""
        if not self.axes:
            return 1.0
        return sum(a.score for a in self.axes) / len(self.axes)


@dataclass
class RadarResult:
    entries: List[RadarEntry] = field(default_factory=list)

    def is_empty(self) -> bool:
        return not self.entries


def _coverage_score(diff: EnvDiff, total_keys: int) -> float:
    """Fraction of keys present in both base and target."""
    if total_keys == 0:
        return 1.0
    missing = len(diff.missing_in_target) + len(diff.missing_in_base)
    return max(0.0, 1.0 - missing / total_keys)


def _consistency_score(diff: EnvDiff, total_keys: int) -> float:
    """Fraction of shared keys with matching values."""
    if total_keys == 0:
        return 1.0
    mismatches = len(diff.mismatched)
    return max(0.0, 1.0 - mismatches / total_keys)


def build_radar(diffs: Sequence[EnvDiff]) -> RadarResult:
    """Build a RadarResult from a list of pairwise EnvDiff objects."""
    result = RadarResult()
    for diff in diffs:
        all_keys = (
            set(diff.base.keys())
            | set(diff.target.keys())
        )
        total = len(all_keys)

        cov = _coverage_score(diff, total)
        con = _consistency_score(diff, total)

        entry = RadarEntry(
            path=diff.target_path,
            axes=[
                RadarAxis("coverage", cov, len(all_keys) - len(diff.missing_in_target) - len(diff.missing_in_base)),
                RadarAxis("consistency", con, total - len(diff.mismatched)),
            ],
        )
        result.entries.append(entry)
    return result
