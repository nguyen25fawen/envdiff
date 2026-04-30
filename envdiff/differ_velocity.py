"""Velocity analysis: measure how rapidly keys change across an ordered sequence of env files."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence

from envdiff.parser import parse_env_file


@dataclass
class VelocityEntry:
    key: str
    values: List[Optional[str]]  # one per file, None if absent
    change_count: int
    first_seen: int  # index of first file where key appears
    last_seen: int   # index of last file where key appears

    @property
    def is_stable(self) -> bool:
        return self.change_count == 0

    @property
    def is_volatile(self) -> bool:
        return self.change_count >= 2


@dataclass
class VelocityResult:
    files: List[str]
    entries: List[VelocityEntry] = field(default_factory=list)

    @property
    def is_empty(self) -> bool:
        return len(self.entries) == 0

    def stable_keys(self) -> List[str]:
        return [e.key for e in self.entries if e.is_stable]

    def volatile_keys(self) -> List[str]:
        return [e.key for e in self.entries if e.is_volatile]

    def by_key(self, key: str) -> Optional[VelocityEntry]:
        for e in self.entries:
            if e.key == key:
                return e
        return None


def _all_keys(envs: List[Dict[str, str]]) -> List[str]:
    keys: set = set()
    for env in envs:
        keys.update(env.keys())
    return sorted(keys)


def build_velocity(paths: Sequence[str]) -> VelocityResult:
    """Parse each file in order and compute per-key change velocity."""
    envs: List[Dict[str, str]] = [parse_env_file(p) for p in paths]
    file_names = list(paths)
    keys = _all_keys(envs)
    entries: List[VelocityEntry] = []

    for key in keys:
        values: List[Optional[str]] = [env.get(key) for env in envs]
        first_seen = next((i for i, v in enumerate(values) if v is not None), 0)
        last_seen = max((i for i, v in enumerate(values) if v is not None), default=0)

        change_count = 0
        prev = values[first_seen]
        for v in values[first_seen + 1 :]:
            if v is not None and v != prev:
                change_count += 1
                prev = v

        entries.append(VelocityEntry(
            key=key,
            values=values,
            change_count=change_count,
            first_seen=first_seen,
            last_seen=last_seen,
        ))

    return VelocityResult(files=file_names, entries=entries)
