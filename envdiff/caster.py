"""Type casting for env values — infer and cast to Python types."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any

_TRUE = {"true", "yes", "1", "on"}
_FALSE = {"false", "no", "0", "off"}


def cast_value(value: str) -> Any:
    """Attempt to cast a string env value to a Python type."""
    if value.lower() in _TRUE:
        return True
    if value.lower() in _FALSE:
        return False
    try:
        return int(value)
    except ValueError:
        pass
    try:
        return float(value)
    except ValueError:
        pass
    return value


def infer_type(value: str) -> str:
    """Return a string label for the inferred type."""
    cast = cast_value(value)
    if isinstance(cast, bool):
        return "bool"
    if isinstance(cast, int):
        return "int"
    if isinstance(cast, float):
        return "float"
    return "str"


@dataclass
class CastResult:
    env: dict[str, str]
    casted: dict[str, Any] = field(default_factory=dict)
    types: dict[str, str] = field(default_factory=dict)


def cast_env(env: dict[str, str]) -> CastResult:
    """Cast all values in an env dict and record inferred types."""
    casted: dict[str, Any] = {}
    types: dict[str, str] = {}
    for key, value in env.items():
        casted[key] = cast_value(value)
        types[key] = infer_type(value)
    return CastResult(env=env, casted=casted, types=types)


def format_cast_result(result: CastResult, show_values: bool = False) -> str:
    lines = []
    for key, typ in result.types.items():
        val = f" = {result.casted[key]!r}" if show_values else ""
        lines.append(f"  {key}: {typ}{val}")
    header = f"Cast result ({len(result.types)} keys):"
    return "\n".join([header] + lines) if lines else "No keys to cast."
