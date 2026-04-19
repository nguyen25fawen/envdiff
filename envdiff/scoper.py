"""Scope filtering: restrict env keys to a named prefix scope."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class ScopeResult:
    scope: str
    matched: Dict[str, str] = field(default_factory=dict)
    stripped: Dict[str, str] = field(default_factory=dict)  # prefix removed


def extract_scope(env: Dict[str, str], scope: str, strip_prefix: bool = True) -> ScopeResult:
    """Return keys that belong to *scope* (case-insensitive prefix match)."""
    prefix = scope.upper().rstrip("_") + "_"
    matched: Dict[str, str] = {}
    stripped: Dict[str, str] = {}
    for key, value in env.items():
        if key.upper().startswith(prefix):
            matched[key] = value
            if strip_prefix:
                short = key[len(prefix):]
            else:
                short = key
            stripped[short] = value
    return ScopeResult(scope=scope, matched=matched, stripped=stripped)


def list_scopes(env: Dict[str, str]) -> List[str]:
    """Return sorted unique first-segment prefixes found in *env* keys."""
    scopes: set[str] = set()
    for key in env:
        if "_" in key:
            scopes.add(key.split("_", 1)[0].upper())
    return sorted(scopes)


def format_scope_result(result: ScopeResult, show_original: bool = False) -> str:
    lines: List[str] = []
    label = result.scope.upper()
    lines.append(f"Scope: {label} ({len(result.matched)} keys)")
    if not result.matched:
        lines.append("  (no keys matched)")
        return "\n".join(lines)
    for orig, short in zip(result.matched.keys(), result.stripped.keys()):
        value = result.matched[orig]
        display = orig if show_original else short
        lines.append(f"  {display}={value}")
    return "\n".join(lines)
