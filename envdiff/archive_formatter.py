"""Formatter for ArchiveResult output."""
from __future__ import annotations

from envdiff.differ_archiver import ArchiveResult


def _c(text: str, code: str) -> str:
    return f"\033[{code}m{text}\033[0m"


def format_archive_rich(result: ArchiveResult, *, color: bool = True) -> str:
    """Return a human-readable multi-line summary of an archive."""
    lines: list[str] = []
    header = f"Archive: {result.label}  [{result.created_at}]"
    lines.append(_c(header, "1;36") if color else header)
    lines.append(_c(f"  Files : {result.total_files}", "0;37") if color else f"  Files : {result.total_files}")
    lines.append(_c(f"  Keys  : {result.total_keys}", "0;37") if color else f"  Keys  : {result.total_keys}")
    lines.append("")
    for entry in result.entries:
        path_line = f"  {entry.path}"
        lines.append(_c(path_line, "1;33") if color else path_line)
        lines.append(f"    keys={entry.key_count}  checksum={entry.checksum}")
    return "\n".join(lines)


def format_archive_summary(result: ArchiveResult) -> str:
    """Return a compact one-line summary suitable for logs."""
    return (
        f"archive '{result.label}': "
        f"{result.total_files} file(s), "
        f"{result.total_keys} total key(s)"
    )
