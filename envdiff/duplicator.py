"""Detect duplicate keys across multiple env files."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List
from envdiff.parser import parse_env_file
from pathlib import Path


@dataclass
class DuplicateResult:
    # key -> list of file paths that define it
    duplicates: Dict[str, List[str]] = field(default_factory=dict)
    all_files: List[str] = field(default_factory=list)


def has_duplicates(result: DuplicateResult) -> bool:
    return bool(result.duplicates)


def find_duplicates(paths: List[str]) -> DuplicateResult:
    """Return keys that appear in more than one file."""
    key_sources: Dict[str, List[str]] = {}
    for p in paths:
        env = parse_env_file(p)
        for key in env:
            key_sources.setdefault(key, []).append(p)
    duplicates = {k: v for k, v in key_sources.items() if len(v) > 1}
    return DuplicateResult(duplicates=duplicates, all_files=list(paths))


def format_duplicate_result(result: DuplicateResult, color: bool = True) -> str:
    def _c(text: str, code: str) -> str:
        return f"\033[{code}m{text}\033[0m" if color else text

    if not has_duplicates(result):
        return _c("No duplicate keys found across files.", "32")

    lines: List[str] = [_c(f"Duplicate keys found ({len(result.duplicates)}):", "33")]
    for key in sorted(result.duplicates):
        sources = result.duplicates[key]
        files_str = ", ".join(sources)
        lines.append(f"  {_c(key, '36')} — defined in: {files_str}")
    return "\n".join(lines)
