"""differ_roster: compare which keys appear across a set of env files.

Produces a roster showing, for each key, which files define it and
which are missing it — useful for auditing key coverage at a glance.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, FrozenSet, List, Sequence

from envdiff.parser import parse_env_file


@dataclass(frozen=True)
class RosterEntry:
    key: str
    present_in: FrozenSet[str]   # file paths (as str) that define the key
    absent_from: FrozenSet[str]  # file paths that are missing the key

    @property
    def coverage(self) -> float:
        total = len(self.present_in) + len(self.absent_from)
        return len(self.present_in) / total if total else 0.0

    @property
    def is_universal(self) -> bool:
        return len(self.absent_from) == 0

    @property
    def is_orphan(self) -> bool:
        return len(self.present_in) == 1


@dataclass
class RosterResult:
    files: List[str]
    entries: List[RosterEntry] = field(default_factory=list)

    def universal_keys(self) -> List[RosterEntry]:
        return [e for e in self.entries if e.is_universal]

    def orphan_keys(self) -> List[RosterEntry]:
        return [e for e in self.entries if e.is_orphan]

    def partial_keys(self) -> List[RosterEntry]:
        return [e for e in self.entries if not e.is_universal and not e.is_orphan]

    def is_empty(self) -> bool:
        return len(self.entries) == 0


def build_roster(paths: Sequence[str | Path]) -> RosterResult:
    """Parse *paths* and build a RosterResult describing key coverage."""
    str_paths = [str(p) for p in paths]
    envs: Dict[str, Dict[str, str]] = {
        sp: parse_env_file(sp) for sp in str_paths
    }

    all_keys: FrozenSet[str] = frozenset(
        k for env in envs.values() for k in env
    )

    entries: List[RosterEntry] = []
    for key in sorted(all_keys):
        present = frozenset(sp for sp, env in envs.items() if key in env)
        absent = frozenset(sp for sp in str_paths if sp not in present)
        entries.append(RosterEntry(key=key, present_in=present, absent_from=absent))

    return RosterResult(files=str_paths, entries=entries)
