"""Rich formatting for cast results."""
from __future__ import annotations
from envdiff.caster import CastResult

_COLORS = {
    "bool": "\033[35m",
    "int": "\033[34m",
    "float": "\033[36m",
    "str": "\033[37m",
}
_RESET = "\033[0m"
_BOLD = "\033[1m"

_TYPE_ICON = {
    "bool": "◈",
    "int": "#",
    "float": "~",
    "str": "\"\"\" ",
}


def _c(text: str, color: str) -> str:
    return f"{color}{text}{_RESET}"


def format_cast_rich(result: CastResult, show_values: bool = False) -> str:
    """Colorized, icon-annotated cast result."""
    if not result.types:
        return _c("No keys to cast.", _COLORS["str"])
    lines = [_BOLD + f"Type inference ({len(result.types)} keys):" + _RESET]
    for key, typ in sorted(result.types.items()):
        color = _COLORS.get(typ, _RESET)
        icon = _TYPE_ICON.get(typ, "?")
        val_part = ""
        if show_values:
            val_part = f" = {result.casted[key]!r}"
        lines.append(f"  {_c(icon, color)} {_BOLD}{key}{_RESET}: {_c(typ, color)}{val_part}")
    return "\n".join(lines)


def format_cast_summary(result: CastResult) -> str:
    """One-line summary of type distribution."""
    from collections import Counter
    counts = Counter(result.types.values())
    parts = [f"{typ}={n}" for typ, n in sorted(counts.items())]
    total = len(result.types)
    return f"Cast summary: {total} keys — " + ", ".join(parts) if parts else "Cast summary: 0 keys"
