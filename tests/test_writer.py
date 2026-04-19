"""Tests for envdiff.writer."""
from __future__ import annotations

import json
import pathlib
import tempfile

import pytest

from envdiff.comparator import DiffResult
from envdiff.reporter import ComparisonReport
from envdiff.writer import write_export


def _make_report() -> ComparisonReport:
    report = ComparisonReport(base_name="base")
    report.diffs["prod"] = DiffResult({"KEY"}, set(), {})
    return report


def test_write_to_file_json(tmp_path):
    out = tmp_path / "result.json"
    write_export(_make_report(), "json", str(out))
    data = json.loads(out.read_text())
    assert data["base"] == "base"


def test_write_to_file_csv(tmp_path):
    out = tmp_path / "result.csv"
    write_export(_make_report(), "csv", str(out))
    content = out.read_text()
    assert "missing_in_target" in content


def test_write_creates_parent_dirs(tmp_path):
    out = tmp_path / "nested" / "dir" / "result.json"
    write_export(_make_report(), "json", str(out))
    assert out.exists()


def test_write_to_stdout_json(capsys):
    write_export(_make_report(), "json", None)
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert data["base"] == "base"


def test_write_to_stdout_csv(capsys):
    write_export(_make_report(), "csv", None)
    captured = capsys.readouterr()
    assert "issue_type" in captured.out


def test_write_unsupported_format_raises(tmp_path):
    """Unsupported format strings should raise a ValueError."""
    out = tmp_path / "result.xml"
    with pytest.raises(ValueError, match="xml"):
        write_export(_make_report(), "xml", str(out))
