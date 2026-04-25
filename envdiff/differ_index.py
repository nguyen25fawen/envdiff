"""Build an inverted index: value -> list of (file, key) pairs.

Useful for spotting when the same value is shared across keys/files,
or when a value has migrated from one key to another.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Tuple

from envdiff.parser import parse_env_file


@dataclass
class IndexEntry:
    value: str
    occurrences: List[Tuple[str, str]] = field(default_factory=list)  # (file, key)

    @property
    def count(self) -> int:
        return len(self.occurrences)

    @property
    def files(self) -> List[str]:
        return sorted({f for f, _ in self.occurrences})

    @property
    def keys(self) -> List[str]:
        return sorted({k for _, k in self.occurrences})

    def is_shared(self) -> bool:
        """True when the value appears in more than one (file, key) pair."""
        return self.count > 1


@dataclass
class IndexResult:
    entries: Dict[str, IndexEntry] = field(default_factory=dict)
    files: List[str] = field(default_factory=list)

    def is_empty(self) -> bool:
        return not self.entries

    def shared_values(self) -> List[IndexEntry]:
        """Return entries whose value appears more than once."""
        return sorted(
            [e for e in self.entries.values() if e.is_shared()],
            key=lambda e: (-e.count, e.value),
        )

    def unique_values(self) -> List[IndexEntry]:
        """Return entries whose value appears exactly once."""
        return sorted(
            [e for e in self.entries.values() if not e.is_shared()],
            key=lambda e: e.value,
        )


def build_index(paths: List[str]) -> IndexResult:
    """Parse each file and build an inverted value -> occurrences index."""
    result = IndexResult(files=list(paths))
    for path in paths:
        env = parse_env_file(path)
        for key, value in env.items():
            if value == "":
                continue
            if value not in result.entries:
                result.entries[value] = IndexEntry(value=value)
            result.entries[value].occurrences.append((path, key))
    return result
