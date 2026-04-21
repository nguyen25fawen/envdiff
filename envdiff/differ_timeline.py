"""Timeline diff: compare a sequence of env snapshots to show how values evolved."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence

from envdiff.parser import parse_env_file


@dataclass
class TimelineEntry:
    """A single point in time for a specific key."""

    label: str
    value: Optional[str]  # None means the key was absent at this point


@dataclass
class KeyTimeline:
    """Evolution of one key across multiple snapshots."""

    key: str
    entries: List[TimelineEntry] = field(default_factory=list)

    @property
    def changed(self) -> bool:
        """Return True if the value (or presence) changed at any point."""
        values = [e.value for e in self.entries]
        return len(set(values)) > 1

    @property
    def first_seen(self) -> Optional[str]:
        """Label of the snapshot where this key first appeared."""
        for entry in self.entries:
            if entry.value is not None:
                return entry.label
        return None

    @property
    def last_seen(self) -> Optional[str]:
        """Label of the snapshot where this key was last present."""
        result = None
        for entry in self.entries:
            if entry.value is not None:
                result = entry.label
        return result


@dataclass
class TimelineResult:
    """Full timeline across all keys and snapshots."""

    labels: List[str]
    timelines: Dict[str, KeyTimeline] = field(default_factory=dict)

    @property
    def all_keys(self) -> List[str]:
        return sorted(self.timelines.keys())

    @property
    def changed_keys(self) -> List[str]:
        """Keys whose value or presence changed across the timeline."""
        return sorted(k for k, t in self.timelines.items() if t.changed)

    @property
    def stable_keys(self) -> List[str]:
        """Keys that remained identical throughout."""
        return sorted(k for k, t in self.timelines.items() if not t.changed)


def build_timeline(
    snapshots: Sequence[Dict[str, str]],
    labels: Optional[Sequence[str]] = None,
) -> TimelineResult:
    """Build a timeline from a sequence of env dicts.

    Args:
        snapshots: Ordered sequence of parsed env dicts.
        labels: Optional human-readable labels (e.g. git tags, dates).
                Defaults to "snapshot-1", "snapshot-2", …

    Returns:
        A TimelineResult describing how each key evolved.
    """
    if labels is None:
        labels = [f"snapshot-{i + 1}" for i in range(len(snapshots))]
    else:
        labels = list(labels)

    if len(labels) != len(snapshots):
        raise ValueError(
            f"labels length ({len(labels)}) must match snapshots length ({len(snapshots)})"
        )

    all_keys: set[str] = set()
    for snap in snapshots:
        all_keys.update(snap.keys())

    result = TimelineResult(labels=labels)

    for key in sorted(all_keys):
        timeline = KeyTimeline(key=key)
        for label, snap in zip(labels, snapshots):
            timeline.entries.append(
                TimelineEntry(label=label, value=snap.get(key))
            )
        result.timelines[key] = timeline

    return result


def build_timeline_from_files(
    paths: Sequence[str],
    labels: Optional[Sequence[str]] = None,
) -> TimelineResult:
    """Convenience wrapper: parse files then build a timeline.

    Args:
        paths: Ordered list of .env file paths.
        labels: Optional labels; defaults to the file paths themselves.

    Returns:
        A TimelineResult.
    """
    if labels is None:
        labels = list(paths)
    snapshots = [parse_env_file(p) for p in paths]
    return build_timeline(snapshots, labels)
