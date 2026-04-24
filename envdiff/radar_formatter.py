"""Formatter for RadarResult – plain-text and rich output."""
from __future__ import annotations

from envdiff.differ_radar import RadarEntry, RadarResult

_RESET = "\033[0m"
_BOLD  = "\033[1m"


def _c(text: str, code: str) -> str:
    return f"{code}{text}{_RESET}"


def _bar(score: float, width: int = 20) -> str:
    filled = round(score * width)
    return "[" + "#" * filled + "-" * (width - filled) + "]"


def _score_color(score: float) -> str:
    if score >= 0.9:
        return "\033[32m"   # green
    if score >= 0.6:
        return "\033[33m"   # yellow
    return "\033[31m"       # red


def _fmt_entry(entry: RadarEntry) -> str:
    lines = [_c(f"  {entry.path}", _BOLD)]
    for axis in entry.axes:
        pct = f"{axis.score * 100:5.1f}%"
        bar = _bar(axis.score)
        colored_bar = _c(bar, _score_color(axis.score))
        lines.append(f"    {axis.name:<14} {colored_bar} {pct}  (raw={axis.raw_value})")
    overall_pct = f"{entry.overall * 100:5.1f}%"
    lines.append(f"    {'overall':<14} {_c(overall_pct, _score_color(entry.overall))}")
    return "\n".join(lines)


def format_radar_rich(result: RadarResult) -> str:
    if result.is_empty():
        return _c("No radar data available.", "\033[90m")
    header = _c("Radar Profile", _BOLD)
    sections = [header]
    for entry in result.entries:
        sections.append(_fmt_entry(entry))
    return "\n".join(sections)


def format_radar_summary(result: RadarResult) -> str:
    if result.is_empty():
        return "radar: no data"
    parts = []
    for entry in result.entries:
        parts.append(f"{entry.path}: overall={entry.overall * 100:.1f}%")
    return "radar: " + " | ".join(parts)
