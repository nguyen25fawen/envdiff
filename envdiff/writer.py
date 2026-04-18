"""Write exported report content to a file or stdout."""
from __future__ import annotations

import pathlib
import sys
from typing import Optional

from envdiff.reporter import ComparisonReport
from envdiff.exporter import export


def write_export(
    report: ComparisonReport,
    fmt: str,
    output_path: Optional[str] = None,
) -> None:
    """Export *report* in *fmt* format and write to *output_path* or stdout."""
    content = export(report, fmt)
    if output_path is None:
        sys.stdout.write(content)
        if not content.endswith("\n"):
            sys.stdout.write("\n")
    else:
        path = pathlib.Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
