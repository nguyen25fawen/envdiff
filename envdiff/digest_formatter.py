"""Formatter for DigestResult output."""
from __future__ import annotations

from typing import List

from envdiff.digester import DigestResult


def _c(text: str, code: str) -> str:
    return f"\033[{code}m{text}\033[0m"


def format_digest_rich(result: DigestResult, *, color: bool = True) -> str:
    """Return a human-readable multi-line report for *result*."""
    lines: List[str] = []

    header = "Env File Digest Report"
    lines.append(_c(header, "1;34") if color else header)
    lines.append("")

    if not result.entries:
        lines.append("  No files digested.")
        return "\n".join(lines)

    reference = result.entries[0].checksum

    for entry in result.entries:
        match = entry.checksum == reference
        icon = _c("✔", "32") if (color and match) else ("✔" if match else (_c("✘", "31") if color else "✘"))
        short = entry.checksum[:12]
        label = _c(short, "32") if (color and match) else (_c(short, "31") if color else short)
        lines.append(f"  {icon}  {entry.path}  [{label}]  ({entry.key_count} keys)")

    return "\n".join(lines)


def format_digest_summary(result: DigestResult, *, color: bool = True) -> str:
    """Return a one-line summary."""
    total = len(result.entries)
    n_conflicts = len(result.conflicts)
    if n_conflicts == 0:
        msg = f"All {total} file(s) share the same digest."
        return _c(msg, "32") if color else msg
    msg = f"{n_conflicts}/{total} file(s) have a differing digest."
    return _c(msg, "31") if color else msg
