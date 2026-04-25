"""Formatter for LensResult output."""
from __future__ import annotations

from typing import List

from envdiff.differ_lens import LensResult


def _c(text: str, code: str) -> str:
    return f"\033[{code}m{text}\033[0m"


def format_lens_rich(result: LensResult, *, show_values: bool = False) -> str:
    lines: List[str] = []
    lines.append(_c(f"Lens: {result.lens.name}", "1;36"))
    lines.append(
        f"  Patterns : {', '.join(result.lens.patterns)}"
    )
    lines.append(
        f"  Matched  : {result.matched_keys} issue(s) out of {result.total_keys} total key(s)"
    )

    focused = result.focused

    if focused.missing_in_second:
        lines.append(_c("  Missing in second:", "33"))
        for k in sorted(focused.missing_in_second):
            lines.append(f"    - {k}")

    if focused.missing_in_first:
        lines.append(_c("  Missing in first:", "33"))
        for k in sorted(focused.missing_in_first):
            lines.append(f"    - {k}")

    if focused.mismatched:
        lines.append(_c("  Mismatched values:", "31"))
        for k in sorted(focused.mismatched):
            if show_values:
                a, b = focused.mismatched[k]
                lines.append(f"    ~ {k}: {a!r} -> {b!r}")
            else:
                lines.append(f"    ~ {k}")

    if result.matched_keys == 0:
        lines.append(_c("  No issues found within this lens.", "32"))

    return "\n".join(lines)


def format_lens_summary(result: LensResult) -> str:
    status = "clean" if result.matched_keys == 0 else f"{result.matched_keys} issue(s)"
    return f"[lens:{result.lens.name}] {status} ({result.matched_keys}/{result.total_keys} matched)"
