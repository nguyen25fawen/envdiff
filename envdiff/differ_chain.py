"""Chain multiple .env files and track how values propagate through the chain."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from envdiff.parser import parse_env_file


@dataclass
class ChainLink:
    path: str
    keys: Dict[str, str]


@dataclass
class ChainEntry:
    key: str
    final_value: str
    origin: str  # path of the file that supplied the final value
    overridden_by: List[str] = field(default_factory=list)  # later files that shadowed it
    introduced_at: str = ""  # first file that defined this key


@dataclass
class ChainResult:
    links: List[ChainLink]
    entries: Dict[str, ChainEntry]

    def all_keys(self) -> List[str]:
        return sorted(self.entries.keys())

    def was_overridden(self, key: str) -> bool:
        entry = self.entries.get(key)
        return bool(entry and entry.overridden_by)

    def origin_of(self, key: str) -> Optional[str]:
        entry = self.entries.get(key)
        return entry.origin if entry else None


def build_chain(paths: List[str], last_wins: bool = False) -> ChainResult:
    """Build a chain result from an ordered list of .env file paths.

    By default the *first* file that defines a key wins (highest precedence).
    Pass ``last_wins=True`` to give the last file highest precedence instead.
    """
    links: List[ChainLink] = [
        ChainLink(path=p, keys=parse_env_file(p)) for p in paths
    ]

    # Collect all keys across all files
    all_keys: set[str] = set()
    for link in links:
        all_keys.update(link.keys)

    entries: Dict[str, ChainEntry] = {}

    ordered = list(reversed(links)) if last_wins else links

    for key in sorted(all_keys):
        introduced_at = ""
        final_value = ""
        origin = ""
        overridden_by: List[str] = []

        for link in links:
            if key in link.keys:
                introduced_at = link.path
                break

        for link in ordered:
            if key in link.keys:
                final_value = link.keys[key]
                origin = link.path
                break

        # Track which files after the winning file also define the key (shadowed)
        winner_idx = next(
            (i for i, lk in enumerate(ordered) if lk.path == origin), 0
        )
        for lk in ordered[winner_idx + 1:]:
            if key in lk.keys:
                overridden_by.append(lk.path)

        entries[key] = ChainEntry(
            key=key,
            final_value=final_value,
            origin=origin,
            overridden_by=overridden_by,
            introduced_at=introduced_at,
        )

    return ChainResult(links=links, entries=entries)
