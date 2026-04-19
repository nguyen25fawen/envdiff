"""Classify env keys by type based on value patterns."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List

_PATTERNS: List[tuple[str, str]] = [
    ("url", r"^https?://"),
    ("path", r"^/[^/]"),
    ("integer", r"^-?\d+$"),
    ("float", r"^-?\d+\.\d+$"),
    ("boolean", r"^(true|false|yes|no|1|0)$"),
    ("uuid", r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"),
    ("empty", r"^$"),
]


def classify_value(value: str) -> str:
    """Return the type label for a given value."""
    v = value.strip()
    for label, pattern in _PATTERNS:
        if re.match(pattern, v, re.IGNORECASE):
            return label
    return "string"


@dataclass
class ClassifiedEnv:
    path: str
    types: Dict[str, str] = field(default_factory=dict)


def classify_env(path: str, env: Dict[str, str]) -> ClassifiedEnv:
    """Classify all keys in an env mapping."""
    result = ClassifiedEnv(path=path)
    for key, value in env.items():
        result.types[key] = classify_value(value)
    return result


def format_classification(classified: ClassifiedEnv) -> str:
    """Return a human-readable classification report."""
    lines = [f"Classification: {classified.path}"]
    if not classified.types:
        lines.append("  (no keys)")
        return "\n".join(lines)
    for key, type_label in sorted(classified.types.items()):
        lines.append(f"  {key}: {type_label}")
    return "\n".join(lines)
