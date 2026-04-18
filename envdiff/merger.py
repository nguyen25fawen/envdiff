"""Merge multiple .env files into a unified template with placeholders."""
from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Optional

from envdiff.parser import parse_env_file


def merge_envs(
    paths: List[Path],
    placeholder: str = "",
    fill_missing: bool = True,
) -> Dict[str, str]:
    """Return a merged dict of all keys found across all env files.

    For each key the value from the *first* file that defines it is used.
    Keys missing in that file receive *placeholder* when fill_missing is True.
    """
    all_parsed: List[Dict[str, str]] = [parse_env_file(p) for p in paths]

    # Collect ordered union of keys (preserve insertion order)
    seen: Dict[str, str] = {}
    for parsed in all_parsed:
        for key, value in parsed.items():
            if key not in seen:
                seen[key] = value

    if not fill_missing:
        return seen

    # Back-fill missing keys with placeholder
    result: Dict[str, str] = {}
    for key in seen:
        # Use value from first file that has it, else placeholder
        value: Optional[str] = None
        for parsed in all_parsed:
            if key in parsed:
                value = parsed[key]
                break
        result[key] = value if value is not None else placeholder

    return result


def render_merged(merged: Dict[str, str]) -> str:
    """Render a merged dict back to .env file content."""
    lines = [f"{key}={value}" for key, value in merged.items()]
    return "\n".join(lines) + ("\n" if lines else "")


def write_merged(merged: Dict[str, str], output: Path) -> None:
    """Write merged env content to *output* path, creating parents as needed."""
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(render_merged(merged), encoding="utf-8")
