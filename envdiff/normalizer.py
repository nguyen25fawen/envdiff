"""Normalize .env key/value pairs for consistent comparison."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class NormalizeResult:
    original: Dict[str, str]
    normalized: Dict[str, str]
    changes: List[str] = field(default_factory=list)


def normalize_keys(env: Dict[str, str], lowercase: bool = False) -> NormalizeResult:
    """Normalize keys: strip whitespace, optionally lowercase."""
    normalized: Dict[str, str] = {}
    changes: List[str] = []
    for k, v in env.items():
        new_k = k.strip()
        if lowercase:
            new_k = new_k.upper()  # canonical: uppercase
        if new_k != k:
            changes.append(f"key '{k}' -> '{new_k}'")
        normalized[new_k] = v
    return NormalizeResult(original=env, normalized=normalized, changes=changes)


def normalize_values(env: Dict[str, str], strip_whitespace: bool = True) -> NormalizeResult:
    """Normalize values: strip surrounding whitespace."""
    normalized: Dict[str, str] = {}
    changes: List[str] = []
    for k, v in env.items():
        new_v = v.strip() if strip_whitespace else v
        if new_v != v:
            changes.append(f"value for '{k}' trimmed")
        normalized[k] = new_v
    return NormalizeResult(original=env, normalized=normalized, changes=changes)


def normalize(env: Dict[str, str], uppercase_keys: bool = True, strip_values: bool = True) -> NormalizeResult:
    """Apply all normalization steps and merge changes."""
    r1 = normalize_keys(env, lowercase=uppercase_keys)
    r2 = normalize_values(r1.normalized, strip_whitespace=strip_values)
    return NormalizeResult(
        original=env,
        normalized=r2.normalized,
        changes=r1.changes + r2.changes,
    )


def format_normalize_result(result: NormalizeResult) -> str:
    if not result.changes:
        return "No normalization changes."
    lines = ["Normalization changes:"]
    for c in result.changes:
        lines.append(f"  • {c}")
    return "\n".join(lines)
