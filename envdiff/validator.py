"""Validate .env file keys against a required keys schema."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable


@dataclass
class ValidationResult:
    missing_required: list[str] = field(default_factory=list)
    unknown_keys: list[str] = field(default_factory=list)

    @property
    def is_valid(self) -> bool:
        return not self.missing_required


def validate(
    env: dict[str, str],
    required: Iterable[str],
    *,
    strict: bool = False,
) -> ValidationResult:
    """Check *env* against *required* keys.

    Args:
        env: Parsed environment mapping.
        required: Collection of keys that must be present.
        strict: When True, also flag keys in *env* not in *required*.

    Returns:
        A :class:`ValidationResult` describing any violations.
    """
    required_set = set(required)
    env_keys = set(env)

    missing = sorted(required_set - env_keys)
    unknown = sorted(env_keys - required_set) if strict else []

    return ValidationResult(missing_required=missing, unknown_keys=unknown)


def load_required_keys(path: str) -> list[str]:
    """Load a plain-text file listing one required key per line.

    Lines starting with '#' and blank lines are ignored.
    """
    keys: list[str] = []
    with open(path, encoding="utf-8") as fh:
        for raw in fh:
            line = raw.strip()
            if line and not line.startswith("#"):
                keys.append(line)
    return keys
