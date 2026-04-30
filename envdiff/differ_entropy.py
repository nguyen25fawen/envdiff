"""Entropy analysis: measure value diversity across .env files."""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Dict, List, Sequence

from envdiff.parser import parse_env_file


@dataclass
class EntropyEntry:
    key: str
    values: List[str]
    unique_count: int
    total_count: int
    entropy: float

    @property
    def is_uniform(self) -> bool:
        return self.unique_count <= 1

    @property
    def is_chaotic(self) -> bool:
        return self.entropy >= 1.0


@dataclass
class EntropyResult:
    entries: List[EntropyEntry] = field(default_factory=list)
    total_files: int = 0

    def is_empty(self) -> bool:
        return not self.entries

    def uniform_keys(self) -> List[EntropyEntry]:
        return [e for e in self.entries if e.is_uniform]

    def chaotic_keys(self) -> List[EntropyEntry]:
        return [e for e in self.entries if e.is_chaotic]


def _shannon(values: List[str]) -> float:
    if not values:
        return 0.0
    total = len(values)
    counts: Dict[str, int] = {}
    for v in values:
        counts[v] = counts.get(v, 0) + 1
    return -sum((c / total) * math.log2(c / total) for c in counts.values())


def build_entropy(paths: Sequence[str]) -> EntropyResult:
    """Parse *paths* and compute per-key Shannon entropy across files."""
    all_envs: List[Dict[str, str]] = [parse_env_file(p) for p in paths]
    all_keys: List[str] = sorted({k for env in all_envs for k in env})

    entries: List[EntropyEntry] = []
    for key in all_keys:
        values = [env[key] for env in all_envs if key in env]
        unique = len(set(values))
        entries.append(
            EntropyEntry(
                key=key,
                values=values,
                unique_count=unique,
                total_count=len(values),
                entropy=_shannon(values),
            )
        )

    return EntropyResult(entries=entries, total_files=len(paths))
