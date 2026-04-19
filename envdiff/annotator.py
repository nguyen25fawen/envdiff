"""Annotate .env files with inline comments describing diff status."""
from __future__ import annotations

from pathlib import Path
from typing import Dict, List

from envdiff.comparator import DiffResult


_ADDED = "# [envdiff] missing in base"
_REMOVED = "# [envdiff] missing in target"
_MISMATCH = "# [envdiff] value mismatch"
_OK = "# [envdiff] ok"


def annotate_lines(
    raw_lines: List[str],
    diff: DiffResult,
    *,
    annotate_ok: bool = False,
) -> List[str]:
    """Return a copy of *raw_lines* with inline diff annotations appended."""
    result: List[str] = []
    for line in raw_lines:
        stripped = line.rstrip()
        if not stripped or stripped.startswith("#"):
            result.append(stripped)
            continue
        if "=" not in stripped:
            result.append(stripped)
            continue
        key = stripped.split("=", 1)[0].strip()
        if key in diff.missing_in_second:
            result.append(f"{stripped}  {_REMOVED}")
        elif key in diff.missing_in_first:
            result.append(f"{stripped}  {_ADDED}")
        elif key in diff.mismatched:
            result.append(f"{stripped}  {_MISMATCH}")
        elif annotate_ok:
            result.append(f"{stripped}  {_OK}")
        else:
            result.append(stripped)
    return result


def annotate_file(
    path: str | Path,
    diff: DiffResult,
    *,
    annotate_ok: bool = False,
) -> str:
    """Read *path* and return annotated text."""
    lines = Path(path).read_text().splitlines()
    annotated = annotate_lines(lines, diff, annotate_ok=annotate_ok)
    return "\n".join(annotated) + "\n"


def write_annotated(
    path: str | Path,
    diff: DiffResult,
    output: str | Path,
    *,
    annotate_ok: bool = False,
) -> None:
    """Write annotated version of *path* to *output*."""
    text = annotate_file(path, diff, annotate_ok=annotate_ok)
    out = Path(output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text)
