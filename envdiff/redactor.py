"""Redact sensitive values from env dicts based on key patterns."""

from __future__ import annotations

import re
from typing import Dict, List

DEFAULT_PATTERNS: List[str] = [
    r"(?i)password",
    r"(?i)secret",
    r"(?i)token",
    r"(?i)api[_]?key",
    r"(?i)private[_]?key",
    r"(?i)auth",
    r"(?i)credential",
]

REDACTED = "***REDACTED***"


def _compile(patterns: List[str]) -> List[re.Pattern]:
    return [re.compile(p) for p in patterns]


def is_sensitive(key: str, patterns: List[re.Pattern]) -> bool:
    """Return True if the key matches any sensitive pattern."""
    return any(p.search(key) for p in patterns)


def redact(
    env: Dict[str, str],
    extra_patterns: List[str] | None = None,
    placeholder: str = REDACTED,
) -> Dict[str, str]:
    """Return a copy of env with sensitive values replaced by placeholder."""
    all_patterns = DEFAULT_PATTERNS + (extra_patterns or [])
    compiled = _compile(all_patterns)
    return {
        key: (placeholder if is_sensitive(key, compiled) else value)
        for key, value in env.items()
    }


def redact_many(
    envs: Dict[str, Dict[str, str]],
    extra_patterns: List[str] | None = None,
    placeholder: str = REDACTED,
) -> Dict[str, Dict[str, str]]:
    """Redact multiple named env dicts."""
    return {
        name: redact(env, extra_patterns=extra_patterns, placeholder=placeholder)
        for name, env in envs.items()
    }


def sensitive_keys(
    env: Dict[str, str],
    extra_patterns: List[str] | None = None,
) -> List[str]:
    """Return a sorted list of keys in env that match sensitive patterns.

    Useful for auditing which keys would be redacted without modifying the dict.

    Args:
        env: The environment dictionary to inspect.
        extra_patterns: Additional regex patterns to consider sensitive.

    Returns:
        A sorted list of matching key names.
    """
    all_patterns = DEFAULT_PATTERNS + (extra_patterns or [])
    compiled = _compile(all_patterns)
    return sorted(key for key in env if is_sensitive(key, compiled))
