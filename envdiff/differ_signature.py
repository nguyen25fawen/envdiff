"""Compute and compare structural signatures for .env files.

A signature captures the sorted set of keys (not values) so two files
can be compared for structural equivalence independently of their values.
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Set

from envdiff.parser import parse_env_file


@dataclass
class SignatureEntry:
    path: str
    keys: List[str]
    signature: str  # hex digest of sorted key names


@dataclass
class SignatureResult:
    entries: List[SignatureEntry] = field(default_factory=list)
    groups: Dict[str, List[str]] = field(default_factory=dict)  # sig -> [path, ...]


def _compute_signature(keys: List[str]) -> str:
    """Return a short hex digest representing the sorted key set."""
    blob = "\n".join(sorted(keys)).encode()
    return hashlib.sha256(blob).hexdigest()[:12]


def build_signature(path: str | Path) -> SignatureEntry:
    """Parse *path* and return its structural signature."""
    env = parse_env_file(str(path))
    keys = sorted(env.keys())
    return SignatureEntry(
        path=str(path),
        keys=keys,
        signature=_compute_signature(keys),
    )


def compare_signatures(paths: List[str | Path]) -> SignatureResult:
    """Build a SignatureResult grouping files by structural equivalence."""
    result = SignatureResult()
    for p in paths:
        entry = build_signature(p)
        result.entries.append(entry)
        result.groups.setdefault(entry.signature, []).append(entry.path)
    return result


def unique_structures(result: SignatureResult) -> int:
    """Return the number of distinct key-set structures found."""
    return len(result.groups)


def structurally_equivalent(result: SignatureResult) -> bool:
    """Return True when every file shares the same key structure."""
    return unique_structures(result) == 1


def differing_keys(
    a: SignatureEntry, b: SignatureEntry
) -> Dict[str, Set[str]]:
    """Return keys only in *a* and keys only in *b*."""
    sa, sb = set(a.keys), set(b.keys)
    return {"only_in_a": sa - sb, "only_in_b": sb - sa}
