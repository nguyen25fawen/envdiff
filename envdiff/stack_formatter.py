"""stack_formatter.py – rich terminal output for StackResult."""
from __future__ import annotations
from typing import List
from envdiff.stacker import StackResult


def _c(text: str, code: str) -> str:
    return f"\033[{code}m{text}\033[0m"


def format_stack_rich(result: StackResult, show_overrides: bool = True) -> str:
    if not result.entries:
        return _c("No keys found in stack.", "33")

    lines: List[str] = []
    header = _c("Stacked ENV", "1;36") + " (" + ", ".join(result.layer_order) + ")"
    lines.append(header)
    lines.append(_c("-" * 50, "90"))

    for key in result.all_keys():
        entry = result.entries[key]
        key_str = _c(key, "1;37")
        val_str = _c(entry.value, "32") if entry.value else _c("(empty)", "33")
        src_str = _c(entry.source, "90")
        lines.append(f"  {key_str} = {val_str}  {src_str}")
        if show_overrides and entry.overridden_by:
            for src, val in entry.overridden_by:
                ov_val = _c(val or "(empty)", "31")
                ov_src = _c(src, "90")
                lines.append(f"    {_c('↳ overridden', '33')} {ov_val}  {ov_src}")

    return "\n".join(lines)


def format_stack_summary(result: StackResult) -> str:
    total = len(result.entries)
    overridden = sum(1 for e in result.entries.values() if e.overridden_by)
    layers = len(result.layer_order)
    parts = [
        _c(f"{layers} layers", "36"),
        _c(f"{total} keys", "32"),
    ]
    if overridden:
        parts.append(_c(f"{overridden} overridden", "33"))
    return "Stack summary: " + ", ".join(parts)
