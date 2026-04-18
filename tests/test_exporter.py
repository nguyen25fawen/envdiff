"""Tests for envdiff.exporter."""
from __future__ import annotations

import csv
import io
import json
import pathlib
import tempfile

import pytest

from envdiff.comparator import DiffResult
from envdiff.reporter import ComparisonReport, build_report
from envdiff.exporter import export, to_csv, to_json


def _make_report() -> ComparisonReport:
    report = ComparisonReport(base_name=".env.base")
    diff = DiffResult(
        missing_in_second={"SECRET"},
        missing_in_first={"EXTRA"},
        mismatched={"PORT": ("8080", "9090")},
    )
    report.diffs["staging"] = diff
    return report


def test_to_json_structure():
    report = _make_report()
    result = json.loads(to_json(report))
    assert result["base"] == ".env.base"
    assert len(result["comparisons"]) == 1
    comp = result["comparisons"][0]
    assert comp["target"] == "staging"
    assert "SECRET" in comp["missing_in_target"]
    assert "EXTRA" in comp["missing_in_base"]
    assert "PORT" in comp["mismatched"]


def test_to_json_no_differences():
    report = ComparisonReport(base_name=".env")
    report.diffs["prod"] = DiffResult(set(), set(), {})
    result = json.loads(to_json(report))
    comp = result["comparisons"][0]
    assert comp["missing_in_target"] == []
    assert comp["missing_in_base"] == []
    assert comp["mismatched"] == []


def test_to_json_multiple_targets():
    """Ensure all targets are included when a report has multiple diffs."""
    report = ComparisonReport(base_name=".env.base")
    report.diffs["staging"] = DiffResult({"A"}, set(), {})
    report.diffs["prod"] = DiffResult(set(), {"B"}, {})
    result = json.loads(to_json(report))
    targets = {comp["target"] for comp in result["comparisons"]}
    assert targets == {"staging", "prod"}


def test_to_csv_headers():
    report = _make_report()
    reader = csv.DictReader(io.StringIO(to_csv(report)))
    assert reader.fieldnames == ["base", "target", "issue_type", "key"]


def test_to_csv_rows():
    report = _make_report()
    rows = list(csv.DictReader(io.StringIO(to_csv(report))))
    issue_types = {r["issue_type"] for r in rows}
    assert "missing_in_target" in issue_types
    assert "missing_in_base" in issue_types
    assert "mismatched" in issue_types


def test_export_json():
    report = _make_report()
    out = export(report, "json")
    assert json.loads(out)["base"] == ".env.base"


def test_export_csv():
    report = _make_report()
    out = export(report, "csv")
    assert "missing_in_target" in out


def test_export_invalid_format():
    report = _make_report()
    with pytest.raises(ValueError, match="Unsupported export format"):
        export(report, "xml")
