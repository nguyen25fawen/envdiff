"""Format DivergenceResult for terminal output."""
from __future__ import annotations

from typing import List

from envdiff.differ_divergence import DivergenceEntry, DivergenceResult


def _c(text: str, code: str) -> str:
    return f"\033[{code}m{text}\033[0m"


def _label(entry: DivergenceEntry) -> str:
    if entry.is_uniform:
        return _c("uniform", "32")
    if entry.is_absent_in_some:
        return _c("absent-in-some", "33")
    return _c(f"{entry.unique_values} variants", "31")


def format_divergence_rich(result: DivergenceResult, show_values: bool = False) -> str:
    if result.is_empty():
        return _c("No keys found across provided files.", "90")

    lines: List[str] = [
        _c(f"Divergence report — {len(result.files)} file(s)", "1"),
        "",
    ]
    for entry in result.entries:
        lines.append(f"  {_c(entry.key, '36')}  {_label(entry)}")
        if show_values:
            for path, val in entry.values.items():
                display = _c("<missing>", "90") if val is None else repr(val)
                lines.append(f"      {_c(path, '90')}: {display}")

    return "\n".join(lines)


def format_divergence_summary(result: DivergenceResult) -> str:
    total = len(result.entries)
    uniform = len(result.uniform_keys())
    diverged = len(result.diverged_keys())
    absent = len(result.absent_keys())

    parts = [
        _c(f"{total} keys", "1"),
        _c(f"{uniform} uniform", "32"),
        _c(f"{diverged} diverged", "31" if diverged else "90"),
        _c(f"{absent} absent-in-some", "33" if absent else "90"),
    ]
    return "  ".join(parts)
