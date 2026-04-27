"""Formatter for GradientResult."""
from __future__ import annotations

from typing import List

from envdiff.differ_gradient import GradientResult


def _c(text: str, code: str) -> str:
    return f"\033[{code}m{text}\033[0m"


def format_gradient_rich(result: GradientResult, *, show_values: bool = False) -> str:
    if result.is_empty:
        return _c("No keys found across provided files.", "90")

    lines: List[str] = [
        _c(f"Gradient report across {len(result.files)} file(s)", "1"),
        "",
    ]

    unstable = result.unstable_keys()
    stable = result.stable_keys()

    if unstable:
        lines.append(_c(f"  Unstable keys ({len(unstable)}):", "33"))
        for entry in unstable:
            tag = _c(f"[{entry.change_count} change(s)]", "31")
            absent_tag = _c(" [missing in some]", "90") if entry.is_absent_in_some else ""
            lines.append(f"    {_c(entry.key, '1')} {tag}{absent_tag}")
            if show_values:
                for i, v in enumerate(entry.values):
                    label = result.files[i]
                    val_str = _c("<absent>", "90") if v is None else _c(repr(v), "36")
                    lines.append(f"      [{i}] {label}: {val_str}")
        lines.append("")

    if stable:
        lines.append(_c(f"  Stable keys ({len(stable)}):", "32"))
        for entry in stable:
            absent_tag = _c(" [missing in some]", "90") if entry.is_absent_in_some else ""
            lines.append(f"    {_c(entry.key, '1')}{absent_tag}")
        lines.append("")

    return "\n".join(lines)


def format_gradient_summary(result: GradientResult) -> str:
    total = len(result.entries)
    unstable = len(result.unstable_keys())
    stable = len(result.stable_keys())
    if total == 0:
        return "gradient: no keys"
    return (
        f"gradient: {total} key(s) across {len(result.files)} file(s) — "
        f"{_c(str(unstable) + ' unstable', '31')}, "
        f"{_c(str(stable) + ' stable', '32')}"
    )
