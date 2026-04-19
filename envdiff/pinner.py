"""Pin current env values to a lockfile for drift detection."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List

from envdiff.parser import parse_env_file

PinData = Dict[str, str]


def pin_env(path: str | Path) -> PinData:
    """Return a dict of key->value from the given env file."""
    return dict(parse_env_file(Path(path)))


def save_pin(data: PinData, output: str | Path) -> None:
    """Write pin data as JSON to *output*."""
    out = Path(output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")


def load_pin(path: str | Path) -> PinData:
    """Load previously saved pin data from a JSON file."""
    return json.loads(Path(path).read_text(encoding="utf-8"))


def diff_pin(
    pinned: PinData, current: PinData
) -> dict[str, list[str]]:
    """Compare pinned values against current values.

    Returns a dict with three keys:
      - 'added':   keys present in current but not in pinned
      - 'removed': keys present in pinned but not in current
      - 'changed': keys whose value differs between pinned and current
    """
    pinned_keys = set(pinned)
    current_keys = set(current)

    added: List[str] = sorted(current_keys - pinned_keys)
    removed: List[str] = sorted(pinned_keys - current_keys)
    changed: List[str] = sorted(
        k for k in pinned_keys & current_keys if pinned[k] != current[k]
    )
    return {"added": added, "removed": removed, "changed": changed}


def format_pin_diff(result: dict[str, list[str]]) -> str:
    """Return a human-readable summary of a pin diff."""
    if not any(result.values()):
        return "\u2705 No drift detected — env matches pinned values."

    lines: List[str] = []
    for key in result["added"]:
        lines.append(f"  + {key}  (new key)")
    for key in result["removed"]:
        lines.append(f"  - {key}  (removed)")
    for key in result["changed"]:
        lines.append(f"  ~ {key}  (value changed)")
    header = f"\u26a0\ufe0f  Drift detected ({len(lines)} change(s)):"
    return "\n".join([header] + lines)
