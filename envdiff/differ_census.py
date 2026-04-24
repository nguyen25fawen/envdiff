"""Census: count how many files each key appears in and compute presence stats."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Sequence

from envdiff.parser import parse_env_file


@dataclass
class CensusEntry:
    key: str
    present_in: List[str]  # file paths where key exists
    absent_from: List[str]  # file paths where key is missing

    @property
    def count(self) -> int:
        return len(self.present_in)

    @property
    def total(self) -> int:
        return len(self.present_in) + len(self.absent_from)

    @property
    def coverage(self) -> float:
        return self.count / self.total if self.total else 0.0

    @property
    def is_universal(self) -> bool:
        return not self.absent_from

    @property
    def is_orphan(self) -> bool:
        return len(self.present_in) == 1


@dataclass
class CensusResult:
    files: List[str]
    entries: List[CensusEntry] = field(default_factory=list)

    def is_empty(self) -> bool:
        return not self.entries

    def universal_keys(self) -> List[CensusEntry]:
        return [e for e in self.entries if e.is_universal]

    def orphan_keys(self) -> List[CensusEntry]:
        return [e for e in self.entries if e.is_orphan]

    def partial_keys(self) -> List[CensusEntry]:
        return [e for e in self.entries if not e.is_universal and not e.is_orphan]


def build_census(paths: Sequence[str | Path]) -> CensusResult:
    """Parse each file and compute per-key presence across all files."""
    str_paths = [str(p) for p in paths]
    envs: Dict[str, Dict[str, str]] = {}
    for p in str_paths:
        envs[p] = parse_env_file(p)

    all_keys: List[str] = sorted({k for env in envs.values() for k in env})
    entries: List[CensusEntry] = []
    for key in all_keys:
        present = [p for p in str_paths if key in envs[p]]
        absent = [p for p in str_paths if key not in envs[p]]
        entries.append(CensusEntry(key=key, present_in=present, absent_from=absent))

    return CensusResult(files=str_paths, entries=entries)
