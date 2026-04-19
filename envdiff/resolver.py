"""Resolve effective env values by merging base with overrides, respecting precedence."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Tuple
from envdiff.parser import parse_env_file


@dataclass
class ResolvedEnv:
    values: Dict[str, str]
    sources: Dict[str, str]  # key -> which file provided the value
    overridden: Dict[str, List[Tuple[str, str]]]  # key -> [(file, value), ...] shadowed


def resolve(files: List[str], *, last_wins: bool = False) -> ResolvedEnv:
    """Merge multiple env files. By default first file wins (highest precedence).

    Args:
        files: ordered list of file paths; index 0 has highest precedence unless last_wins.
        last_wins: if True, later files override earlier ones.
    """
    if last_wins:
        files = list(reversed(files))

    values: Dict[str, str] = {}
    sources: Dict[str, str] = {}
    overridden: Dict[str, List[Tuple[str, str]]] = {}

    for path in files:
        parsed = parse_env_file(path)
        for key, val in parsed.items():
            if key not in values:
                values[key] = val
                sources[key] = path
            else:
                overridden.setdefault(key, []).append((path, val))

    return ResolvedEnv(values=values, sources=sources, overridden=overridden)


def format_resolved(resolved: ResolvedEnv, *, show_sources: bool = False) -> str:
    lines = []
    for key in sorted(resolved.values):
        val = resolved.values[key]
        if show_sources:
            src = resolved.sources[key]
            lines.append(f"{key}={val}  # from {src}")
        else:
            lines.append(f"{key}={val}")
        if key in resolved.overridden:
            for shadow_file, shadow_val in resolved.overridden[key]:
                lines.append(f"  # shadowed in {shadow_file}: {key}={shadow_val}")
    return "\n".join(lines)
