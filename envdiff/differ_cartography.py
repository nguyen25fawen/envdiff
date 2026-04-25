"""Cartography: map which files define, share, or omit each key."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, FrozenSet, List, Sequence

from envdiff.parser import parse_env_file


@dataclass
class CartographyEntry:
    key: str
    defined_in: List[str]          # file paths where key exists
    missing_from: List[str]        # file paths where key is absent
    values: Dict[str, str]         # path -> value

    @property
    def is_universal(self) -> bool:
        return len(self.missing_from) == 0

    @property
    def is_orphan(self) -> bool:
        return len(self.defined_in) == 1

    @property
    def is_uniform(self) -> bool:
        return len(set(self.values.values())) <= 1


@dataclass
class CartographyResult:
    files: List[str]
    entries: List[CartographyEntry]

    def is_empty(self) -> bool:
        return len(self.entries) == 0

    def universal_keys(self) -> List[CartographyEntry]:
        return [e for e in self.entries if e.is_universal]

    def orphan_keys(self) -> List[CartographyEntry]:
        return [e for e in self.entries if e.is_orphan]

    def conflicted_keys(self) -> List[CartographyEntry]:
        return [e for e in self.entries if not e.is_uniform and e.is_universal]


def build_cartography(paths: Sequence[str]) -> CartographyResult:
    """Parse all files and build a key-level map across environments."""
    file_envs: Dict[str, Dict[str, str]] = {}
    for p in paths:
        file_envs[p] = parse_env_file(Path(p))

    all_keys: FrozenSet[str] = frozenset(
        k for env in file_envs.values() for k in env
    )

    entries: List[CartographyEntry] = []
    for key in sorted(all_keys):
        defined_in = [p for p in paths if key in file_envs[p]]
        missing_from = [p for p in paths if key not in file_envs[p]]
        values = {p: file_envs[p][key] for p in defined_in}
        entries.append(CartographyEntry(
            key=key,
            defined_in=defined_in,
            missing_from=missing_from,
            values=values,
        ))

    return CartographyResult(files=list(paths), entries=entries)
