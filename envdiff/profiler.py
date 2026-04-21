"""Profile .env files to summarize key statistics."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List

from envdiff.parser import parse_env_file


@dataclass
class EnvProfile:
    path: str
    total_keys: int
    empty_values: List[str] = field(default_factory=list)
    duplicate_keys: List[str] = field(default_factory=list)
    longest_key: str = ""
    longest_value_key: str = ""


def profile_env(path: str | Path) -> EnvProfile:
    """Parse a .env file and return a statistical profile.

    Args:
        path: Path to the .env file to profile.

    Returns:
        An EnvProfile summarising key statistics of the file.

    Raises:
        FileNotFoundError: If the given path does not exist.
        ValueError: If the path points to a directory rather than a file.
    """
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"No such file: '{p}'")
    if not p.is_file():
        raise ValueError(f"Path is not a file: '{p}'")

    raw_lines: Dict[str, int] = {}
    duplicates: List[str] = []
    empty: List[str] = []

    for line in p.read_text().splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if "=" not in stripped:
            continue
        key = stripped.split("=", 1)[0].strip()
        raw_lines[key] = raw_lines.get(key, 0) + 1
        if raw_lines[key] > 1 and key not in duplicates:
            duplicates.append(key)

    parsed: Dict[str, str] = parse_env_file(p)

    for k, v in parsed.items():
        if v == "":
            empty.append(k)

    longest_key = max(parsed.keys(), key=len, default="")
    longest_value_key = max(parsed.keys(), key=lambda k: len(parsed[k]), default="")

    return EnvProfile(
        path=str(path),
        total_keys=len(parsed),
        empty_values=sorted(empty),
        duplicate_keys=sorted(duplicates),
        longest_key=longest_key,
        longest_value_key=longest_value_key,
    )


def format_profile(profile: EnvProfile) -> str:
    """Return a human-readable summary of an EnvProfile."""
    lines = [
        f"File : {profile.path}",
        f"Keys : {profile.total_keys}",
        f"Empty values ({len(profile.empty_values)}): {', '.join(profile.empty_values) or 'none'}",
        f"Duplicates   ({len(profile.duplicate_keys)}): {', '.join(profile.duplicate_keys) or 'none'}",
        f"Longest key  : {profile.longest_key or 'n/a'}",
        f"Longest value: {profile.longest_value_key or 'n/a'}",
    ]
    return "\n".join(lines)
