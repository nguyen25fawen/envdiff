"""Format an IndexResult for terminal output."""
from __future__ import annotations

from envdiff.differ_index import IndexResult


def _c(code: str, text: str) -> str:
    return f"\033[{code}m{text}\033[0m"


def format_index_rich(result: IndexResult, show_unique: bool = False) -> str:
    if result.is_empty():
        return _c("32", "No indexed values found.")

    lines: list[str] = []
    lines.append(_c("1;34", f"Value Index — {len(result.files)} file(s)"))
    lines.append("")

    shared = result.shared_values()
    if shared:
        lines.append(_c("1;33", f"Shared values ({len(shared)}):"))
        for entry in shared:
            masked = "*" * min(len(entry.value), 8)
            lines.append(f"  {_c('33', masked)}  [{entry.count} occurrences]")
            for file_path, key in sorted(entry.occurrences):
                lines.append(f"    {_c('36', key)}  in  {_c('90', file_path)}")
        lines.append("")
    else:
        lines.append(_c("32", "No shared values detected."))
        lines.append("")

    if show_unique:
        unique = result.unique_values()
        lines.append(_c("1", f"Unique values ({len(unique)}):"))
        for entry in unique:
            file_path, key = entry.occurrences[0]
            lines.append(f"  {_c('36', key)}  in  {_c('90', file_path)}")
        lines.append("")

    return "\n".join(lines)


def format_index_summary(result: IndexResult) -> str:
    total = len(result.entries)
    shared = len(result.shared_values())
    unique = total - shared
    parts = [
        _c("1", "Index summary:"),
        f"  Total distinct values : {total}",
        f"  Shared values         : {_c('33', str(shared)) if shared else str(shared)}",
        f"  Unique values         : {unique}",
    ]
    return "\n".join(parts)
