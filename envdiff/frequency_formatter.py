"""Formatters for FrequencyResult."""
from __future__ import annotations

from envdiff.differ_frequency import FrequencyResult


def _c(text: str, code: str) -> str:
    return f"\033[{code}m{text}\033[0m"


def _bar(fraction: float, width: int = 20) -> str:
    filled = round(fraction * width)
    return "█" * filled + "░" * (width - filled)


def _freq_color(fraction: float) -> str:
    if fraction == 1.0:
        return "32"   # green
    if fraction >= 0.5:
        return "33"   # yellow
    return "31"        # red


def format_frequency_rich(result: FrequencyResult, *, show_files: bool = False) -> str:
    if result.is_empty():
        return _c("No keys found.", "90")

    lines = [
        _c(f"Key Frequency  ({result.total_files} file(s))", "1;36"),
        "",
    ]

    for entry in result.entries:
        pct = f"{entry.frequency * 100:5.1f}%"
        bar = _bar(entry.frequency)
        color = _freq_color(entry.frequency)
        label = _c(f"{entry.count}/{entry.total}", color)
        lines.append(f"  {_c(entry.key, '1'):<40} {label}  {pct}  {bar}")
        if show_files:
            for f in entry.files:
                lines.append(f"      {_c(f, '90')}")

    return "\n".join(lines)


def format_frequency_summary(result: FrequencyResult) -> str:
    universal = len(result.universal_keys())
    rare = len(result.rare_keys())
    total_keys = len(result.entries)
    lines = [
        _c("Frequency Summary", "1;36"),
        f"  Total keys : {total_keys}",
        f"  Universal  : {_c(str(universal), '32')}",
        f"  Rare (<50%): {_c(str(rare), '31')}",
    ]
    return "\n".join(lines)
