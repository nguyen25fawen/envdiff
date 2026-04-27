"""Gradient analysis: measure how much an env key's value changes across a sequence of files."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence

from envdiff.parser import parse_env_file


@dataclass
class GradientEntry:
    key: str
    values: List[Optional[str]]  # one slot per file; None = absent
    change_count: int = 0
    first_value: Optional[str] = None
    last_value: Optional[str] = None

    @property
    def is_stable(self) -> bool:
        """True when the key never changes across files."""
        return self.change_count == 0

    @property
    def is_absent_in_some(self) -> bool:
        return any(v is None for v in self.values)


@dataclass
class GradientResult:
    files: List[str]
    entries: List[GradientEntry] = field(default_factory=list)

    @property
    def is_empty(self) -> bool:
        return len(self.entries) == 0

    def unstable_keys(self) -> List[GradientEntry]:
        return [e for e in self.entries if not e.is_stable]

    def stable_keys(self) -> List[GradientEntry]:
        return [e for e in self.entries if e.is_stable]


def _count_changes(values: List[Optional[str]]) -> int:
    changes = 0
    prev = values[0]
    for v in values[1:]:
        if v != prev:
            changes += 1
        prev = v
    return changes


def build_gradient(paths: Sequence[str]) -> GradientResult:
    """Parse *paths* in order and compute per-key value gradients."""
    envs: List[Dict[str, str]] = [parse_env_file(p) for p in paths]
    all_keys: List[str] = sorted({k for env in envs for k in env})
    entries: List[GradientEntry] = []

    for key in all_keys:
        values: List[Optional[str]] = [env.get(key) for env in envs]
        changes = _count_changes(values)
        present = [v for v in values if v is not None]
        entry = GradientEntry(
            key=key,
            values=values,
            change_count=changes,
            first_value=present[0] if present else None,
            last_value=present[-1] if present else None,
        )
        entries.append(entry)

    return GradientResult(files=list(paths), entries=entries)
