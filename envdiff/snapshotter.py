"""Snapshot .env state to JSON for drift detection over time."""
from __future__ import annotations

import json
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from envdiff.parser import parse_env_file


def _hash_env(env: dict[str, str]) -> str:
    serialized = json.dumps(env, sort_keys=True)
    return hashlib.sha256(serialized.encode()).hexdigest()[:16]


def take_snapshot(env_path: str | Path, label: str | None = None) -> dict[str, Any]:
    """Parse an env file and return a snapshot dict."""
    path = Path(env_path)
    env = parse_env_file(path)
    return {
        "label": label or path.name,
        "source": str(path),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "hash": _hash_env(env),
        "keys": sorted(env.keys()),
        "entries": env,
    }


def save_snapshot(snapshot: dict[str, Any], output: str | Path) -> None:
    """Write snapshot to a JSON file."""
    out = Path(output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(snapshot, indent=2))


def load_snapshot(path: str | Path) -> dict[str, Any]:
    """Load a previously saved snapshot."""
    return json.loads(Path(path).read_text())


def diff_snapshots(
    old: dict[str, Any], new: dict[str, Any]
) -> dict[str, Any]:
    """Compare two snapshots and return a drift report."""
    old_entries = old.get("entries", {})
    new_entries = new.get("entries", {})
    old_keys = set(old_entries)
    new_keys = set(new_entries)

    added = sorted(new_keys - old_keys)
    removed = sorted(old_keys - new_keys)
    changed = sorted(
        k for k in old_keys & new_keys if old_entries[k] != new_entries[k]
    )

    return {
        "old_label": old.get("label"),
        "new_label": new.get("label"),
        "old_timestamp": old.get("timestamp"),
        "new_timestamp": new.get("timestamp"),
        "added": added,
        "removed": removed,
        "changed": changed,
        "drift_detected": bool(added or removed or changed),
    }
