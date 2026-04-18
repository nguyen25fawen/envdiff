"""Patch a target .env file by adding keys missing from the base."""
from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Optional

from envdiff.parser import parse_env_file


def patch_env(
    base: Dict[str, str],
    target: Dict[str, str],
    placeholder: str = "",
) -> Dict[str, str]:
    """Return a copy of *target* with missing keys added (set to *placeholder*)."""
    patched = dict(target)
    for key, value in base.items():
        if key not in patched:
            patched[key] = placeholder
    return patched


def patch_file(
    base_path: Path,
    target_path: Path,
    output_path: Optional[Path] = None,
    placeholder: str = "",
    dry_run: bool = False,
) -> List[str]:
    """Patch *target_path* with keys from *base_path*.

    Returns list of keys that were added.
    When *dry_run* is True the file is not written.
    When *output_path* is None the target file is updated in-place.
    """
    base = parse_env_file(base_path)
    target = parse_env_file(target_path)

    added = [k for k in base if k not in target]
    if not added:
        return []

    patched = patch_env(base, target, placeholder=placeholder)

    if not dry_run:
        dest = output_path or target_path
        dest.parent.mkdir(parents=True, exist_ok=True)
        lines = [f"{k}={v}" for k, v in patched.items()]
        dest.write_text("\n".join(lines) + "\n", encoding="utf-8")

    return sorted(added)
