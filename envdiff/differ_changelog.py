"""Build a human-readable changelog between two snapshots of .env files."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class ChangelogEntry:
    key: str
    kind: str          # "added" | "removed" | "changed"
    old_value: Optional[str] = None
    new_value: Optional[str] = None


@dataclass
class ChangelogResult:
    base_label: str
    target_label: str
    entries: List[ChangelogEntry] = field(default_factory=list)

    def is_empty(self) -> bool:
        return len(self.entries) == 0

    def by_kind(self, kind: str) -> List[ChangelogEntry]:
        return [e for e in self.entries if e.kind == kind]


def build_changelog(
    base: Dict[str, str],
    target: Dict[str, str],
    base_label: str = "base",
    target_label: str = "target",
    redact: bool = True,
) -> ChangelogResult:
    """Compare two env dicts and return a structured changelog."""
    result = ChangelogResult(base_label=base_label, target_label=target_label)
    all_keys = sorted(set(base) | set(target))

    for key in all_keys:
        in_base = key in base
        in_target = key in target

        if in_base and not in_target:
            result.entries.append(
                ChangelogEntry(key=key, kind="removed",
                               old_value=None if redact else base[key])
            )
        elif not in_base and in_target:
            result.entries.append(
                ChangelogEntry(key=key, kind="added",
                               new_value=None if redact else target[key])
            )
        elif base[key] != target[key]:
            result.entries.append(
                ChangelogEntry(
                    key=key,
                    kind="changed",
                    old_value=None if redact else base[key],
                    new_value=None if redact else target[key],
                )
            )

    return result
