"""Formatter for VelocityResult."""
from __future__ import annotations

from envdiff.differ_velocity import VelocityResult


def _c(text: str, code: str) -> str:
    return f"\033[{code}m{text}\033[0m"


def _velocity_color(change_count: int) -> str:
    if change_count == 0:
        return "32"   # green  – stable
    if change_count == 1:
        return "33"   # yellow – moderate
    return "31"       # red    – volatile


def _bar(change_count: int, max_changes: int, width: int = 10) -> str:
    if max_changes == 0:
        return "." * width
    filled = round(change_count / max_changes * width)
    return "#" * filled + "." * (width - filled)


def format_velocity_rich(result: VelocityResult, *, show_values: bool = False) -> str:
    if result.is_empty:
        return "No keys found."

    lines = [_c(f"Velocity report ({len(result.files)} files)", "1")]
    lines.append(_c("  {:<30}  {:>7}  {}".format("KEY", "CHANGES", "TREND"), "2"))

    max_changes = max((e.change_count for e in result.entries), default=0)

    for entry in result.entries:
        color = _velocity_color(entry.change_count)
        bar = _bar(entry.change_count, max_changes)
        label = _c(entry.key, color)
        lines.append(f"  {label:<39}  {entry.change_count:>7}  {bar}")
        if show_values:
            for i, v in enumerate(entry.values):
                fname = result.files[i]
                display = v if v is not None else _c("(absent)", "2")
                lines.append(f"      [{i}] {fname}: {display}")

    return "\n".join(lines)


def format_velocity_summary(result: VelocityResult) -> str:
    total = len(result.entries)
    stable = len(result.stable_keys())
    volatile = len(result.volatile_keys())
    moderate = total - stable - volatile
    return (
        f"Velocity: {total} keys across {len(result.files)} files — "
        f"{_c(str(stable), '32')} stable, "
        f"{_c(str(moderate), '33')} moderate, "
        f"{_c(str(volatile), '31')} volatile"
    )
