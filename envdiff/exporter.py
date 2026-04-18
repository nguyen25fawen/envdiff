"""Export comparison results to different output formats."""
from __future__ import annotations

import csv
import io
import json
from typing import List

from envdiff.reporter import ComparisonReport


def to_json(report: ComparisonReport, indent: int = 2) -> str:
    """Serialize a ComparisonReport to a JSON string."""
    data: dict = {
        "base": report.base_name,
        "comparisons": [],
    }
    for target_name, diff in report.diffs.items():
        entry = {
            "target": target_name,
            "missing_in_target": sorted(diff.missing_in_second),
            "missing_in_base": sorted(diff.missing_in_first),
            "mismatched": sorted(diff.mismatched.keys()),
        }
        data["comparisons"].append(entry)
    return json.dumps(data, indent=indent)


def to_csv(report: ComparisonReport) -> str:
    """Serialize a ComparisonReport to a CSV string."""
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["base", "target", "issue_type", "key"])
    for target_name, diff in report.diffs.items():
        for key in sorted(diff.missing_in_second):
            writer.writerow([report.base_name, target_name, "missing_in_target", key])
        for key in sorted(diff.missing_in_first):
            writer.writerow([report.base_name, target_name, "missing_in_base", key])
        for key in sorted(diff.mismatched.keys()):
            writer.writerow([report.base_name, target_name, "mismatched", key])
    return output.getvalue()


def export(report: ComparisonReport, fmt: str) -> str:
    """Export report in the requested format ('json' or 'csv')."""
    if fmt == "json":
        return to_json(report)
    if fmt == "csv":
        return to_csv(report)
    raise ValueError(f"Unsupported export format: {fmt!r}. Choose 'json' or 'csv'.")
