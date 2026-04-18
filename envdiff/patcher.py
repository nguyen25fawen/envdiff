"""Apply patches to env files: add missing keys, update values."""
from __future__ import annotations

from pathlib import Path
from typing import Mapping

from envdiff.parser import parse_env_file


def patch_env(
    original: Mapping[str, str],
    patch: Mapping[str, str],
    overwrite: bool = False,
) -> dict[str, str]:
    """Return a new env dict with *patch* applied to *original*.

    If *overwrite* is False (default) only missing keys are added.
    If *overwrite* is True existing keys are also updated.
    """
    result = dict(original)
    for key, value in patch.items():
        if overwrite or key not in result:
            result[key] = value
    return result


def patch_file(
    target: str | Path,
    patch: Mapping[str, str],
    overwrite: bool = False,
    output: str | Path | None = None,
) -> Path:
    """Read *target*, apply *patch*, write result to *output* (or in-place).

    Returns the path that was written.
    """
    target = Path(target)
    original = parse_env_file(target)
    patched = patch_env(original, patch, overwrite=overwrite)

    out_path = Path(output) if output else target
    out_path.parent.mkdir(parents=True, exist_ok=True)

    lines: list[str] = []
    for key, value in patched.items():
        # Quote values that contain spaces
        if " " in value:
            lines.append(f'{key}="{value}"')
        else:
            lines.append(f"{key}={value}")

    out_path.write_text("\n".join(lines) + "\n")
    return out_path
