"""Compute value divergence metrics across multiple .env files."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from envdiff.parser import parse_env_file


@dataclass
class DivergenceEntry:
    key: str
    values: Dict[str, Optional[str]]  # file_path -> value
    unique_values: int = 0
    is_uniform: bool = False
    is_absent_in_some: bool = False


@dataclass
class DivergenceResult:
    files: List[str]
    entries: List[DivergenceEntry] = field(default_factory=list)

    def is_empty(self) -> bool:
        return len(self.entries) == 0

    def uniform_keys(self) -> List[str]:
        return [e.key for e in self.entries if e.is_uniform]

    def diverged_keys(self) -> List[str]:
        return [e.key for e in self.entries if not e.is_uniform]

    def absent_keys(self) -> List[str]:
        return [e.key for e in self.entries if e.is_absent_in_some]


def _all_keys(envs: List[Dict[str, str]]) -> List[str]:
    keys: set = set()
    for env in envs:
        keys.update(env.keys())
    return sorted(keys)


def build_divergence(file_paths: List[str]) -> DivergenceResult:
    envs = [parse_env_file(p) for p in file_paths]
    result = DivergenceResult(files=list(file_paths))

    for key in _all_keys(envs):
        values: Dict[str, Optional[str]] = {
            path: env.get(key) for path, env in zip(file_paths, envs)
        }
        present_values = [v for v in values.values() if v is not None]
        unique = len(set(present_values))
        entry = DivergenceEntry(
            key=key,
            values=values,
            unique_values=unique,
            is_uniform=(unique == 1 and len(present_values) == len(file_paths)),
            is_absent_in_some=any(v is None for v in values.values()),
        )
        result.entries.append(entry)

    return result
