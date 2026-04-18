"""Utilities for sorting and grouping diff results by severity."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from envdiff.comparator import DiffResult


@dataclass
class GroupedDiffs:
    missing_in_second: List[str] = field(default_factory=list)
    missing_in_first: List[str] = field(default_factory=list)
    mismatched: List[str] = field(default_factory=list)

    def all_keys(self) -> List[str]:
        """Return all affected keys across every group, sorted."""
        combined = (
            self.missing_in_second
            + self.missing_in_first
            + self.mismatched
        )
        return sorted(set(combined))

    def is_empty(self) -> bool:
        return not (self.missing_in_second or self.missing_in_first or self.mismatched)


def group_diffs(result: DiffResult) -> GroupedDiffs:
    """Partition a DiffResult into a GroupedDiffs by category."""
    return GroupedDiffs(
        missing_in_second=sorted(result.missing_in_second),
        missing_in_first=sorted(result.missing_in_first),
        mismatched=sorted(result.mismatched.keys()),
    )


def sort_keys_by_severity(result: DiffResult) -> List[str]:
    """Return keys ordered: missing_in_second, missing_in_first, mismatched.

    Within each tier keys are sorted alphabetically.
    This ordering surfaces the most critical issues first.
    """
    grouped = group_diffs(result)
    return (
        grouped.missing_in_second
        + grouped.missing_in_first
        + grouped.mismatched
    )
