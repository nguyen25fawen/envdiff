"""trimmer.py — strip unused keys from an env file based on a reference set."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List

from envdiff.parser import parse_env_file


@dataclass
class TrimResult:
    kept: Dict[str, str] = field(default_factory=dict)
    removed: List[str] = field(default_factory=list)

    @property
    def any_removed(self) -> bool:
        return bool(self.removed)


def trim_env(
    env: Dict[str, str],
    reference: Dict[str, str],
) -> TrimResult:
    """Return a TrimResult keeping only keys present in *reference*."""
    kept: Dict[str, str] = {}
    removed: List[str] = []
    for key, value in env.items():
        if key in reference:
            kept[key] = value
        else:
            removed.append(key)
    return TrimResult(kept=kept, removed=sorted(removed))


def trim_files(
    target_path: Path,
    reference_path: Path,
) -> TrimResult:
    """Parse both files and trim *target* to keys found in *reference*."""
    target = parse_env_file(target_path)
    reference = parse_env_file(reference_path)
    return trim_env(target, reference)


def render_trimmed(result: TrimResult) -> str:
    """Render the kept keys as .env file content."""
    lines = [f"{k}={v}" for k, v in result.kept.items()]
    return "\n".join(lines) + ("\n" if lines else "")


def write_trimmed(result: TrimResult, dest: Path) -> None:
    """Write the trimmed env to *dest*, creating parent directories as needed."""
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(render_trimmed(result))
