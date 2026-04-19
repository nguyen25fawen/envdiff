"""Formatter for DiffStats output."""
from __future__ import annotations
from envdiff.differ_stats import DiffStats


def _c(text: str, code: str) -> str:
    return f"\033[{code}m{text}\033[0m"


def format_stats_rich(stats: DiffStats) -> str:
    lines: list[str] = []
    lines.append(_c("=== Diff Statistics ===", "1;36"))
    lines.append(f"  Pairs compared : {stats.total_pairs}")
    lines.append(f"  Total issues   : {_c(str(stats.total_issues), '1;31') if stats.total_issues else _c('0', '1;32')}")
    lines.append(f"  Missing in target : {stats.total_missing_in_target}")
    lines.append(f"  Missing in base   : {stats.total_missing_in_base}")
    lines.append(f"  Mismatched values : {stats.total_mismatched}")

    if stats.keys_always_missing:
        lines.append(_c("\nKeys missing in ALL targets:", "1;33"))
        for k in stats.keys_always_missing:
            lines.append(f"  - {k}")

    if stats.keys_always_mismatched:
        lines.append(_c("\nKeys mismatched in ALL pairs:", "1;33"))
        for k in stats.keys_always_mismatched:
            lines.append(f"  ~ {k}")

    return "\n".join(lines)


def format_stats_summary(stats: DiffStats) -> str:
    if stats.total_issues == 0:
        return _c("All pairs clean — no issues found.", "1;32")
    parts = []
    if stats.total_missing_in_target:
        parts.append(f"{stats.total_missing_in_target} missing-in-target")
    if stats.total_missing_in_base:
        parts.append(f"{stats.total_missing_in_base} missing-in-base")
    if stats.total_mismatched:
        parts.append(f"{stats.total_mismatched} mismatched")
    return _c(f"Issues across {stats.total_pairs} pair(s): ", "1;33") + ", ".join(parts) + "."
