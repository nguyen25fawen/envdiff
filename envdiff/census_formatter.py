"""Rich-text and summary formatting for CensusResult."""
from __future__ import annotations

from envdiff.differ_census import CensusResult


def _c(text: str, code: str) -> str:
    return f"\033[{code}m{text}\033[0m"


def format_census_rich(result: CensusResult, *, show_absent: bool = False) -> str:
    if result.is_empty():
        return _c("No keys found across provided files.", "33")

    lines = [_c(f"Key Census — {len(result.files)} file(s)", "1;36"), ""]

    universal = result.universal_keys()
    orphans = result.orphan_keys()
    partial = result.partial_keys()

    sections = [
        (_c("Universal keys", "1;32"), universal),
        (_c("Partial keys", "1;33"), partial),
        (_c("Orphan keys", "1;31"), orphans),
    ]

    for label, entries in sections:
        if not entries:
            continue
        lines.append(label)
        for e in entries:
            bar = f"{e.count}/{e.total}"
            pct = f"{e.coverage * 100:.0f}%"
            lines.append(f"  {e.key:<40} {bar:>6}  ({pct})")  
            if show_absent and e.absent_from:
                for path in e.absent_from:
                    lines.append(_c(f"    missing: {path}", "90"))
        lines.append("")

    return "\n".join(lines).rstrip()


def format_census_summary(result: CensusResult) -> str:
    total = len(result.entries)
    universal = len(result.universal_keys())
    orphans = len(result.orphan_keys())
    partial = len(result.partial_keys())
    return (
        f"Census: {total} keys total — "
        f"{universal} universal, {partial} partial, {orphans} orphan"
    )
