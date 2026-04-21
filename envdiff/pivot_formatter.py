"""Rich-text and plain-text formatting for PivotResult."""
from __future__ import annotations

from typing import List

from envdiff.differ_pivot import PivotResult

_RESET = "\033[0m"
_BOLD = "\033[1m"
_RED = "\033[31m"
_GREEN = "\033[32m"
_YELLOW = "\033[33m"
_CYAN = "\033[36m"
_DIM = "\033[2m"


def _c(color: str, text: str) -> str:
    return f"{color}{text}{_RESET}"


_ABSENT = _c(_DIM, "<absent>")
_MASKED = _c(_DIM, "***")


def format_pivot_rich(
    result: PivotResult,
    *,
    show_values: bool = False,
    only_conflicts: bool = False,
) -> str:
    lines: List[str] = []
    header = _c(_BOLD, f"Pivot view — {len(result.files)} file(s), {len(result.rows)} key(s)")
    lines.append(header)
    lines.append("")

    rows = result.conflicted_rows() if only_conflicts else result.rows
    if not rows:
        lines.append(_c(_GREEN, "  ✔ No conflicts found."))
        return "\n".join(lines)

    col_w = max((len(f) for f in result.files), default=10)
    key_w = max((len(r.key) for r in rows), default=10)

    header_row = "  " + _c(_CYAN, "KEY".ljust(key_w)) + "  " + "  ".join(
        _c(_CYAN, f.ljust(col_w)) for f in result.files
    )
    lines.append(header_row)
    lines.append("  " + "-" * (key_w + 2 + (col_w + 2) * len(result.files)))

    for row in rows:
        color = _GREEN if row.is_uniform else _YELLOW if row.is_universal else _RED
        key_col = _c(color, row.key.ljust(key_w))
        val_cols: List[str] = []
        for cell in row.cells:
            if cell.value is None:
                val_cols.append(_ABSENT.ljust(col_w))
            elif show_values:
                val_cols.append(cell.value[:col_w].ljust(col_w))
            else:
                val_cols.append(_MASKED.ljust(col_w))
        lines.append("  " + key_col + "  " + "  ".join(val_cols))

    return "\n".join(lines)


def format_pivot_summary(result: PivotResult) -> str:
    total = len(result.rows)
    conflicts = len(result.conflicted_rows())
    missing = len(result.missing_rows())
    if conflicts == 0 and missing == 0:
        return _c(_GREEN, f"Pivot: {total} key(s), no conflicts.")
    parts = []
    if conflicts:
        parts.append(_c(_YELLOW, f"{conflicts} conflict(s)"))
    if missing:
        parts.append(_c(_RED, f"{missing} key(s) absent in ≥1 file"))
    return f"Pivot: {total} key(s) — " + ", ".join(parts) + "."
