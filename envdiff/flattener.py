"""Flatten nested key structures and expand prefixed groups into flat env dicts."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class FlattenResult:
    original: Dict[str, str]
    flattened: Dict[str, str]
    renamed: Dict[str, str]  # old_key -> new_key
    separator: str = "__"


def any_renamed(result: FlattenResult) -> bool:
    return bool(result.renamed)


def flatten_env(
    env: Dict[str, str],
    separator: str = "__",
    lowercase: bool = False,
) -> FlattenResult:
    """Flatten keys by collapsing repeated separators and optionally lowercasing."""
    flattened: Dict[str, str] = {}
    renamed: Dict[str, str] = {}

    for key, value in env.items():
        new_key = key
        # collapse multiple consecutive separators
        while separator * 2 in new_key:
            new_key = new_key.replace(separator * 2, separator)
        # strip leading/trailing separator
        new_key = new_key.strip(separator)
        if lowercase:
            new_key = new_key.lower()
        if new_key != key:
            renamed[key] = new_key
        flattened[new_key] = value

    return FlattenResult(
        original=dict(env),
        flattened=flattened,
        renamed=renamed,
        separator=separator,
    )


def format_flatten_result(result: FlattenResult, *, show_unchanged: bool = False) -> str:
    lines: List[str] = []
    if not any_renamed(result):
        lines.append("No keys were renamed during flattening.")
        return "\n".join(lines)

    lines.append(f"Flattened {len(result.renamed)} key(s):")
    for old, new in sorted(result.renamed.items()):
        lines.append(f"  {old}  ->  {new}")

    if show_unchanged:
        unchanged = [k for k in result.flattened if k not in result.renamed.values() or k in result.renamed]
        unchanged_keys = set(result.original) - set(result.renamed)
        if unchanged_keys:
            lines.append(f"Unchanged: {', '.join(sorted(unchanged_keys))}")

    return "\n".join(lines)
