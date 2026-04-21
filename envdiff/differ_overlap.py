"""Compute key overlap statistics across multiple .env files."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, FrozenSet, List, Set

from envdiff.parser import parse_env_file


@dataclass
class OverlapResult:
    files: List[str]
    all_keys: FrozenSet[str]
    # key -> set of file paths that contain it
    key_presence: Dict[str, Set[str]] = field(default_factory=dict)

    @property
    def universal_keys(self) -> FrozenSet[str]:
        """Keys present in every file."""
        if not self.files:
            return frozenset()
        return frozenset(
            k for k, paths in self.key_presence.items() if len(paths) == len(self.files)
        )

    @property
    def exclusive_keys(self) -> Dict[str, str]:
        """Keys that appear in exactly one file; maps key -> that file path."""
        result: Dict[str, str] = {}
        for k, paths in self.key_presence.items():
            if len(paths) == 1:
                result[k] = next(iter(paths))
        return result

    @property
    def partial_keys(self) -> FrozenSet[str]:
        """Keys present in more than one but not all files."""
        total = len(self.files)
        return frozenset(
            k
            for k, paths in self.key_presence.items()
            if 1 < len(paths) < total
        )

    def coverage(self, key: str) -> float:
        """Fraction of files that contain *key* (0.0 – 1.0)."""
        if not self.files:
            return 0.0
        return len(self.key_presence.get(key, set())) / len(self.files)


def compute_overlap(paths: List[str]) -> OverlapResult:
    """Parse each file and build an OverlapResult."""
    envs: Dict[str, Dict[str, str]] = {}
    for p in paths:
        envs[p] = parse_env_file(Path(p))

    all_keys: Set[str] = set()
    for env in envs.values():
        all_keys.update(env.keys())

    key_presence: Dict[str, Set[str]] = {k: set() for k in all_keys}
    for p, env in envs.items():
        for k in env:
            key_presence[k].add(p)

    return OverlapResult(
        files=list(paths),
        all_keys=frozenset(all_keys),
        key_presence=key_presence,
    )
