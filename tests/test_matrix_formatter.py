"""Tests for envdiff.matrix_formatter."""
from __future__ import annotations

import pathlib

from envdiff.differ_matrix import build_matrix
from envdiff.matrix_formatter import format_matrix_table, format_matrix_summary


def _write(tmp_path: pathlib.Path, name: str, content: str) -> str:
    p = tmp_path / name
    p.write_text(content)
    return str(p)


def test_table_contains_key_name(tmp_path):
    a = _write(tmp_path, "a.env", "MYKEY=hello\n")
    b = _write(tmp_path, "b.env", "MYKEY=world\n")
    result = build_matrix([a, b])
    table = format_matrix_table(result)
    assert "MYKEY" in table


def test_table_shows_missing_label(tmp_path):
    a = _write(tmp_path, "a.env", "FOO=1\n")
    b = _write(tmp_path, "b.env", "OTHER=2\n")
    result = build_matrix([a, b])
    table = format_matrix_table(result)
    assert "MISSING" in table


def test_table_masks_values_by_default(tmp_path):
    a = _write(tmp_path, "a.env", "SECRET=hunter2\n")
    b = _write(tmp_path, "b.env", "SECRET=hunter2\n")
    result = build_matrix([a, b])
    table = format_matrix_table(result)
    assert "hunter2" not in table
    assert "*****" in table


def test_table_shows_values_when_unmasked(tmp_path):
    a = _write(tmp_path, "a.env", "PORT=8080\n")
    b = _write(tmp_path, "b.env", "PORT=9090\n")
    result = build_matrix([a, b])
    table = format_matrix_table(result, mask_values=False)
    assert "8080" in table
    assert "9090" in table


def test_summary_no_issues(tmp_path):
    a = _write(tmp_path, "a.env", "KEY=val\n")
    b = _write(tmp_path, "b.env", "KEY=val\n")
    result = build_matrix([a, b])
    summary = format_matrix_summary(result)
    assert "No issues" in summary


def test_summary_reports_missing(tmp_path):
    a = _write(tmp_path, "a.env", "FOO=1\nBAR=2\n")
    b = _write(tmp_path, "b.env", "FOO=1\n")
    result = build_matrix([a, b])
    summary = format_matrix_summary(result)
    assert "missing" in summary.lower()
    assert "BAR" in summary


def test_summary_reports_conflicts(tmp_path):
    a = _write(tmp_path, "a.env", "ENV=production\n")
    b = _write(tmp_path, "b.env", "ENV=staging\n")
    result = build_matrix([a, b])
    summary = format_matrix_summary(result)
    assert "conflict" in summary.lower()
    assert "ENV" in summary


def test_summary_contains_file_count(tmp_path):
    a = _write(tmp_path, "a.env", "K=1\n")
    b = _write(tmp_path, "b.env", "K=1\n")
    c = _write(tmp_path, "c.env", "K=1\n")
    result = build_matrix([a, b, c])
    summary = format_matrix_summary(result)
    assert "3 files" in summary
