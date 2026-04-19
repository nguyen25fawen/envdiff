"""Format rename detection results for terminal output."""
from __future__ import annotations
from typing import List
from envdiff.renamer import RenameResult

_RESET = "\033[0m"
_YELLOW = "\033[33m"
_GREEN = "\033[32m"
_RED = "\033[31m"
_BOLD = "\033[1m"


def _c(color: str, text: str) -> str:
    return f"{color}{text}{_RESET}"


def format_rename_result(result: RenameResult, *, color: bool = True) -> str:
    lines: List[str] = []

    if not result.confirmed and not result.unmatched_old and not result.unmatched_new:
        msg = "No rename candidates detected."
        return _c(_GREEN, msg) if color else msg

    if result.confirmed:
        header = "Likely renames (matched by value):"
        lines.append(_c(_BOLD, header) if color else header)
        for c in result.confirmed:
            arrow = f"  {c.old_key}  ->  {c.new_key}"
            lines.append(_c(_YELLOW, arrow) if color else arrow)

    if result.unmatched_old:
        header = "Keys removed (no value match found):"
        lines.append(_c(_BOLD, header) if color else header)
        for k in result.unmatched_old:
            line = f"  - {k}"
            lines.append(_c(_RED, line) if color else line)

    if result.unmatched_new:
        header = "Keys added (no value match found):"
        lines.append(_c(_BOLD, header) if color else header)
        for k in result.unmatched_new:
            line = f"  + {k}"
            lines.append(_c(_GREEN, line) if color else line)

    return "\n".join(lines)
