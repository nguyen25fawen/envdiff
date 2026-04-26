"""Track the lineage (origin and evolution) of keys across an ordered list of env files."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from envdiff.parser import parse_env_file


@dataclass
class LineageEntry:
    key: str
    first_seen_in: str
    last_seen_in: str
    all_sources: List[str]
    values_by_source: Dict[str, str]
    changed: bool  # True if value differs across any two sources that define it

    @property
    def source_count(self) -> int:
        return len(self.all_sources)

    def value_at(self, path: str) -> Optional[str]:
        return self.values_by_source.get(path)


@dataclass
class LineageResult:
    files: List[str]
    entries: List[LineageEntry] = field(default_factory=list)

    def is_empty(self) -> bool:
        return len(self.entries) == 0

    def changed_keys(self) -> List[LineageEntry]:
        return [e for e in self.entries if e.changed]

    def stable_keys(self) -> List[LineageEntry]:
        return [e for e in self.entries if not e.changed]

    def orphan_keys(self) -> List[LineageEntry]:
        """Keys that appear in exactly one file."""
        return [e for e in self.entries if e.source_count == 1]


def build_lineage(paths: List[str]) -> LineageResult:
    """Build a lineage map for all keys found across *paths* (ordered)."""
    parsed: List[tuple[str, Dict[str, str]]] = [
        (p, parse_env_file(p)) for p in paths
    ]

    all_keys: List[str] = sorted(
        {k for _, env in parsed for k in env}
    )

    entries: List[LineageEntry] = []
    for key in all_keys:
        sources = [(p, env[key]) for p, env in parsed if key in env]
        values_by_source = {p: v for p, v in sources}
        source_paths = [p for p, _ in sources]
        values = [v for _, v in sources]
        changed = len(set(values)) > 1
        entries.append(
            LineageEntry(
                key=key,
                first_seen_in=source_paths[0],
                last_seen_in=source_paths[-1],
                all_sources=source_paths,
                values_by_source=values_by_source,
                changed=changed,
            )
        )

    return LineageResult(files=list(paths), entries=entries)
