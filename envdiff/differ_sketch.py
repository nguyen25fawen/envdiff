"""Probabilistic key-set sketch comparison using MinHash-style fingerprints."""
from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from typing import Dict, List, Sequence


@dataclass
class SketchEntry:
    path: str
    keys: List[str]
    fingerprint: List[int]  # band hashes
    sketch_size: int


@dataclass
class SketchResult:
    entries: List[SketchEntry] = field(default_factory=list)
    similarity_matrix: Dict[str, Dict[str, float]] = field(default_factory=dict)

    def is_empty(self) -> bool:
        return len(self.entries) == 0


def _minhash(keys: Sequence[str], num_hashes: int = 64) -> List[int]:
    """Compute a MinHash signature for a set of keys."""
    if not keys:
        return [0] * num_hashes
    minimums: List[int] = []
    for i in range(num_hashes):
        seed = i.to_bytes(4, "little")
        min_val = None
        for k in keys:
            digest = hashlib.md5(seed + k.encode()).digest()
            val = int.from_bytes(digest[:4], "little")
            if min_val is None or val < min_val:
                min_val = val
        minimums.append(min_val or 0)
    return minimums


def _jaccard_from_minhash(a: List[int], b: List[int]) -> float:
    if not a or not b:
        return 0.0
    matches = sum(x == y for x, y in zip(a, b))
    return matches / len(a)


def build_sketch(env_files: Dict[str, Dict[str, str]], num_hashes: int = 64) -> SketchResult:
    """Build MinHash sketches for each env file and compute pairwise similarity."""
    entries: List[SketchEntry] = []
    for path, env in env_files.items():
        keys = sorted(env.keys())
        fp = _minhash(keys, num_hashes)
        entries.append(SketchEntry(path=path, keys=keys, fingerprint=fp, sketch_size=num_hashes))

    matrix: Dict[str, Dict[str, float]] = {}
    for i, a in enumerate(entries):
        matrix[a.path] = {}
        for j, b in enumerate(entries):
            if i == j:
                matrix[a.path][b.path] = 1.0
            else:
                sim = _jaccard_from_minhash(a.fingerprint, b.fingerprint)
                matrix[a.path][b.path] = round(sim, 4)

    return SketchResult(entries=entries, similarity_matrix=matrix)
