"""Summarize multiple env files into a unified key statistics report."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List
from envdiff.parser import parse_env_file


@dataclass
class KeyStat:
    key: str
    present_in: List[str] = field(default_factory=list)
    missing_in: List[str] = field(default_factory=list)
    unique_values: int = 0
    has_empty: bool = False


@dataclass
class EnvSummary:
    files: List[str]
    stats: Dict[str, KeyStat]

    def total_keys(self) -> int:
        return len(self.stats)

    def universal_keys(self) -> List[str]:
        """Keys present in every file."""
        return [k for k, s in self.stats.items() if not s.missing_in]

    def partial_keys(self) -> List[str]:
        """Keys missing in at least one file."""
        return [k for k, s in self.stats.items() if s.missing_in]


def summarize(paths: List[str]) -> EnvSummary:
    envs: Dict[str, Dict[str, str]] = {}
    for p in paths:
        envs[p] = parse_env_file(p)

    all_keys: set[str] = set()
    for data in envs.values():
        all_keys.update(data.keys())

    stats: Dict[str, KeyStat] = {}
    for key in sorted(all_keys):
        values = []
        present_in = []
        missing_in = []
        has_empty = False
        for path, data in envs.items():
            if key in data:
                present_in.append(path)
                val = data[key]
                values.append(val)
                if val == "":
                    has_empty = True
            else:
                missing_in.append(path)
        stats[key] = KeyStat(
            key=key,
            present_in=present_in,
            missing_in=missing_in,
            unique_values=len(set(values)),
            has_empty=has_empty,
        )

    return EnvSummary(files=list(paths), stats=stats)
