"""Formatters for the diff matrix output."""
from __future__ import annotations

import os
from typing import List

from envdiff.differ_matrix import MatrixResult, matrix_missing_pairs, matrix_value_conflicts

_RESET = "\033[0m"
_RED = "\033[31m"
_YELLOW = "\033[33m"
_GREEN = "\033[32m"
_BOLD = "\033[1m"
_DIM = "\033[2m"


def _c(text: str, *codes: str) -> str:
    if not os.isatty(1):
        return text
    return "".join(codes) + text + _RESET


def format_matrix_table(result: MatrixResult, *, mask_values: bool = True) -> str:
    """Render an ASCII table of keys vs files."""
    short_names = [os.path.basename(f) for f in result.files]
    col_w = max((len(n) for n in short_names), default=6)
    key_w = max((len(k) for k in result.keys), default=3)

    header = _c("KEY".ljust(key_w), _BOLD) + "  " + "  ".join(
        _c(n.ljust(col_w), _BOLD) for n in short_names
    )
    sep = "-" * (key_w + 2 + (col_w + 2) * len(short_names))

    lines: List[str] = [header, sep]
    for key in result.keys:
        cells = result.rows[key]
        parts: List[str] = []
        for cell in cells:
            if not cell.present:
                parts.append(_c("MISSING".ljust(col_w), _RED))
            elif mask_values:
                parts.append(_c("*****".ljust(col_w), _DIM))
            else:
                parts.append((cell.value or "").ljust(col_w))
        row_key = key.ljust(key_w)
        lines.append(row_key + "  " + "  ".join(parts))

    return "\n".join(lines)


def format_matrix_summary(result: MatrixResult) -> str:
    """Short text summary of matrix issues."""
    missing = matrix_missing_pairs(result)
    conflicts = matrix_value_conflicts(result)
    total_keys = len(result.keys)
    total_files = len(result.files)

    lines: List[str] = [
        _c(f"Matrix: {total_keys} keys across {total_files} files", _BOLD),
    ]
    if not missing and not conflicts:
        lines.append(_c("  ✔ No issues found.", _GREEN))
        return "\n".join(lines)

    if missing:
        lines.append(_c(f"  ✖ {len(missing)} missing key/file pair(s):", _RED))
        for key, fpath in missing:
            lines.append(f"      {key}  ←  {os.path.basename(fpath)}")

    if conflicts:
        lines.append(_c(f"  ⚠ {len(conflicts)} key(s) with conflicting values:", _YELLOW))
        for key, vals in conflicts:
            lines.append(f"      {key}: {', '.join(repr(v) for v in vals)}")

    return "\n".join(lines)
