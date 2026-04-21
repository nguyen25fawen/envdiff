"""Formatter for HeatmapResult."""
from __future__ import annotations

from envdiff.differ_heatmap import HeatmapResult, HeatmapEntry

_RESET = "\033[0m"
_BOLD = "\033[1m"


def _c(text: str, code: str) -> str:
    return f"{code}{text}{_RESET}"


_HEAT_COLOR = {
    "hot": "\033[91m",    # bright red
    "warm": "\033[93m",   # yellow
    "cool": "\033[92m",   # green
}

_HEAT_ICON = {"hot": "🔥", "warm": "🌡 ", "cool": "❄ "}


def _fmt_entry(e: HeatmapEntry, show_counts: bool) -> str:
    color = _HEAT_COLOR[e.heat]
    icon = _HEAT_ICON[e.heat]
    label = _c(e.key, _BOLD)
    heat_label = _c(e.heat.upper(), color)
    if show_counts:
        detail = f"  miss={e.miss_count} mismatch={e.mismatch_count} total={e.total}"
    else:
        detail = f"  total={e.total}"
    return f"  {icon} {label}  [{heat_label}]{detail}"


def format_heatmap_rich(
    result: HeatmapResult,
    top: int = 10,
    show_counts: bool = True,
) -> str:
    lines: list[str] = []
    lines.append(_c(f"Key Heatmap  ({result.total_pairs} pair(s) analysed)", _BOLD))
    if result.is_empty():
        lines.append("  " + _c("No differences found across any pair.", "\033[92m"))
        return "\n".join(lines)
    for entry in result.hottest(top):
        lines.append(_fmt_entry(entry, show_counts))
    return "\n".join(lines)


def format_heatmap_summary(result: HeatmapResult) -> str:
    total_keys = len(result.entries)
    hot = sum(1 for e in result.entries if e.heat == "hot")
    warm = sum(1 for e in result.entries if e.heat == "warm")
    return (
        f"Heatmap: {total_keys} key(s) with differences "
        f"({hot} hot, {warm} warm) across {result.total_pairs} pair(s)."
    )
