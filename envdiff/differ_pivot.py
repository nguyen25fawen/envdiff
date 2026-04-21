"""Pivot a multi-file diff into a per-key view across all files."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from envdiff.parser import parse_env_file


@dataclass
class PivotCell:
    file: str
    value: Optional[str]  # None means key is absent


@dataclass
class PivotRow:
    key: str
    cells: List[PivotCell] = field(default_factory=list)

    @property
    def is_uniform(self) -> bool:
        """True when every file that has the key shares the same value."""
        present = [c.value for c in self.cells if c.value is not None]
        return len(set(present)) <= 1

    @property
    def is_universal(self) -> bool:
        """True when the key exists in every file."""
        return all(c.value is not None for c in self.cells)


@dataclass
class PivotResult:
    files: List[str]
    rows: List[PivotRow] = field(default_factory=list)

    def uniform_rows(self) -> List[PivotRow]:
        return [r for r in self.rows if r.is_uniform]

    def conflicted_rows(self) -> List[PivotRow]:
        return [r for r in self.rows if not r.is_uniform]

    def missing_rows(self) -> List[PivotRow]:
        return [r for r in self.rows if not r.is_universal]


def pivot_files(paths: List[str]) -> PivotResult:
    """Load *paths* and return a PivotResult keyed by every distinct key."""
    envs: List[Dict[str, str]] = [parse_env_file(p) for p in paths]
    all_keys: List[str] = sorted({k for env in envs for k in env})

    rows: List[PivotRow] = []
    for key in all_keys:
        cells = [
            PivotCell(file=path, value=env.get(key))
            for path, env in zip(paths, envs)
        ]
        rows.append(PivotRow(key=key, cells=cells))

    return PivotResult(files=list(paths), rows=rows)
