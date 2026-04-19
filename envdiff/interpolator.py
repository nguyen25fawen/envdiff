"""Detect and resolve variable interpolation in .env files."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional

_REF_RE = re.compile(r"\$\{([^}]+)\}|\$([A-Za-z_][A-Za-z0-9_]*)")


@dataclass
class InterpolationResult:
    resolved: Dict[str, str] = field(default_factory=dict)
    unresolved: Dict[str, List[str]] = field(default_factory=dict)  # key -> missing refs
    references: Dict[str, List[str]] = field(default_factory=dict)  # key -> refs used


def _refs(value: str) -> List[str]:
    return [m[0] or m[1] for m in _REF_RE.findall(value)]


def _resolve_value(value: str, env: Dict[str, str], seen: Optional[set] = None) -> Optional[str]:
    if seen is None:
        seen = set()

    def replacer(m: re.Match) -> str:
        ref = m.group(1) or m.group(2)
        if ref in seen:
            raise ValueError(f"Circular reference: {ref}")
        if ref not in env:
            raise KeyError(ref)
        seen.add(ref)
        result = _resolve_value(env[ref], env, seen)
        seen.discard(ref)
        if result is None:
            raise KeyError(ref)
        return result

    try:
        return _REF_RE.sub(replacer, value)
    except (KeyError, ValueError):
        return None


def interpolate(env: Dict[str, str]) -> InterpolationResult:
    result = InterpolationResult()
    for key, value in env.items():
        refs = _refs(value)
        if refs:
            result.references[key] = refs
        resolved = _resolve_value(value, env)
        if resolved is not None:
            result.resolved[key] = resolved
        else:
            missing = [r for r in refs if r not in env]
            result.unresolved[key] = missing if missing else refs
            result.resolved[key] = value  # keep original
    # keys with no interpolation
    for key, value in env.items():
        if key not in result.resolved:
            result.resolved[key] = value
    return result
