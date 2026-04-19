"""Detect drift between a reference .env and one or more target files."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from envdiff.parser import parse_env_file


@dataclass
class DriftEntry:
    key: str
    base_value: str | None
    target_value: str | None
    kind: str  # 'added' | 'removed' | 'changed'


@dataclass
class DriftReport:
    base: str
    target: str
    entries: List[DriftEntry] = field(default_factory=list)

    def has_drift(self) -> bool:
        return bool(self.entries)

    def by_kind(self, kind: str) -> List[DriftEntry]:
        return [e for e in self.entries if e.kind == kind]


def drift_pair(base_path: str, target_path: str, check_values: bool = True) -> DriftReport:
    base = parse_env_file(base_path)
    target = parse_env_file(target_path)
    entries: List[DriftEntry] = []

    all_keys = sorted(set(base) | set(target))
    for key in all_keys:
        in_base = key in base
        in_target = key in target
        if in_base and not in_target:
            entries.append(DriftEntry(key, base[key], None, "removed"))
        elif in_target and not in_base:
            entries.append(DriftEntry(key, None, target[key], "added"))
        elif check_values and base[key] != target[key]:
            entries.append(DriftEntry(key, base[key], target[key], "changed"))

    return DriftReport(base=base_path, target=target_path, entries=entries)


def drift_many(base_path: str, target_paths: List[str], check_values: bool = True) -> List[DriftReport]:
    return [drift_pair(base_path, t, check_values=check_values) for t in target_paths]
