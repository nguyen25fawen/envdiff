"""Frequency analysis: count how often each key appears across multiple env files."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List

from envdiff.parser import parse_env_file


@dataclass
class FrequencyEntry:
    key: str
    count: int
    total: int
    files: List[str] = field(default_factory=list)

    @property
    def frequency(self) -> float:
        """Fraction of files that contain this key (0.0 – 1.0)."""
        return self.count / self.total if self.total else 0.0

    @property
    def is_universal(self) -> bool:
        return self.count == self.total

    @property
    def is_rare(self) -> bool:
        """Key appears in fewer than half the files."""
        return self.frequency < 0.5


@dataclass
class FrequencyResult:
    entries: List[FrequencyEntry] = field(default_factory=list)
    total_files: int = 0

    def is_empty(self) -> bool:
        return len(self.entries) == 0

    def universal_keys(self) -> List[FrequencyEntry]:
        return [e for e in self.entries if e.is_universal]

    def rare_keys(self) -> List[FrequencyEntry]:
        return [e for e in self.entries if e.is_rare]


def build_frequency(paths: List[str]) -> FrequencyResult:
    """Analyse how frequently each key appears across *paths*."""
    total = len(paths)
    key_files: Dict[str, List[str]] = {}

    for path in paths:
        env = parse_env_file(Path(path))
        for key in env:
            key_files.setdefault(key, []).append(path)

    entries = [
        FrequencyEntry(
            key=key,
            count=len(files),
            total=total,
            files=sorted(files),
        )
        for key, files in sorted(key_files.items())
    ]

    return FrequencyResult(entries=entries, total_files=total)
