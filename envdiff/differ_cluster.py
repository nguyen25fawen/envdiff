"""Cluster .env files by similarity based on shared keys and values."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, FrozenSet, List, Tuple

from envdiff.parser import parse_env_file


@dataclass
class ClusterEntry:
    path: str
    keys: FrozenSet[str]
    shared_with: Dict[str, float] = field(default_factory=dict)  # path -> similarity


@dataclass
class ClusterResult:
    entries: List[ClusterEntry]
    groups: List[List[str]]  # each inner list is a cluster of paths

    def is_empty(self) -> bool:
        return len(self.entries) == 0


def _jaccard(a: FrozenSet[str], b: FrozenSet[str]) -> float:
    """Jaccard similarity between two sets of keys."""
    if not a and not b:
        return 1.0
    union = a | b
    if not union:
        return 0.0
    return len(a & b) / len(union)


def _build_entries(files: List[str]) -> List[ClusterEntry]:
    entries: List[ClusterEntry] = []
    parsed = [(p, frozenset(parse_env_file(p).keys())) for p in files]
    for path, keys in parsed:
        entry = ClusterEntry(path=path, keys=keys)
        entries.append(entry)
    for i, (p1, k1) in enumerate(parsed):
        for j, (p2, k2) in enumerate(parsed):
            if i >= j:
                continue
            sim = _jaccard(k1, k2)
            entries[i].shared_with[p2] = sim
            entries[j].shared_with[p1] = sim
    return entries


def _group_by_threshold(
    entries: List[ClusterEntry], threshold: float
) -> List[List[str]]:
    """Simple greedy clustering: group files whose similarity >= threshold."""
    visited: set = set()
    groups: List[List[str]] = []
    paths = [e.path for e in entries]
    sim_map = {e.path: e.shared_with for e in entries}

    for path in paths:
        if path in visited:
            continue
        group = [path]
        visited.add(path)
        for other in paths:
            if other in visited:
                continue
            if sim_map[path].get(other, 0.0) >= threshold:
                group.append(other)
                visited.add(other)
        groups.append(sorted(group))
    return groups


def cluster_files(files: List[str], threshold: float = 0.5) -> ClusterResult:
    """Cluster env files by key-set similarity."""
    if not files:
        return ClusterResult(entries=[], groups=[])
    entries = _build_entries(files)
    groups = _group_by_threshold(entries, threshold)
    return ClusterResult(entries=entries, groups=groups)
