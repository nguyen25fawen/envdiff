"""Formatter for WatchlistResult."""
from __future__ import annotations

from envdiff.differ_watchlist import WatchlistResult


def _c(text: str, code: str) -> str:
    return f"\033[{code}m{text}\033[0m"


_KIND_LABEL = {
    "missing_in_second": ("MISSING →", "31"),
    "missing_in_first": ("← MISSING", "33"),
    "mismatch": ("MISMATCH", "35"),
}


def format_watchlist_rich(result: WatchlistResult) -> str:
    lines: list[str] = []
    lines.append(_c("Watchlist Report", "1;36"))
    lines.append(_c(f"  Patterns: {len(result.patterns)}", "2"))

    if result.is_empty():
        lines.append(_c("  ✓ No watchlist keys affected.", "32"))
        return "\n".join(lines)

    lines.append("")
    for hit in result.hits:
        label, color = _KIND_LABEL.get(hit.kind, (hit.kind, "37"))
        lines.append(
            f"  {_c(label, color)}  {_c(hit.key, '1')}  "
            f"{_c(f'(pattern: {hit.pattern})', '2')}"
        )

    return "\n".join(lines)


def format_watchlist_summary(result: WatchlistResult) -> str:
    total = len(result.hits)
    if total == 0:
        return "watchlist: no hits"
    kinds = {}
    for h in result.hits:
        kinds[h.kind] = kinds.get(h.kind, 0) + 1
    parts = ", ".join(f"{v} {k}" for k, v in sorted(kinds.items()))
    return f"watchlist: {total} hit(s) — {parts}"
