"""Tests for envdiff.reporter."""
from __future__ import annotations

import os
import pytest

from envdiff.reporter import build_report, ComparisonReport
from envdiff.comparator import DiffResult


def _write(tmp_path, name: str, content: str) -> str:
    p = tmp_path / name
    p.write_text(content)
    return str(p)


def test_build_report_no_differences(tmp_path):
    base = _write(tmp_path, ".env.base", "KEY1=val1\nKEY2=val2\n")
    target = _write(tmp_path, ".env.prod", "KEY1=val1\nKEY2=val2\n")
    report = build_report(base, [target])
    assert not report.any_differences
    assert str(target) in report.results


def test_build_report_missing_key(tmp_path):
    base = _write(tmp_path, ".env.base", "KEY1=val1\nKEY2=val2\n")
    target = _write(tmp_path, ".env.prod", "KEY1=val1\n")
    report = build_report(base, [target])
    assert report.any_differences
    result = report.results[str(target)]
    assert "KEY2" in result.missing_in_second


def test_build_report_multiple_targets(tmp_path):
    base = _write(tmp_path, ".env.base", "A=1\nB=2\n")
    t1 = _write(tmp_path, ".env.t1", "A=1\nB=2\n")
    t2 = _write(tmp_path, ".env.t2", "A=1\n")
    report = build_report(base, [t1, t2])
    assert not report.results[t1].has_differences
    assert report.results[t2].has_differences
    assert report.any_differences


def test_summary_lines_contains_base(tmp_path):
    base = _write(tmp_path, ".env.base", "X=1\n")
    target = _write(tmp_path, ".env.prod", "X=1\n")
    report = build_report(base, [target])
    lines = report.summary_lines()
    assert lines[0].startswith("Base:")
    assert str(base) in lines[0]


def test_summary_lines_ok_status(tmp_path):
    base = _write(tmp_path, ".env.base", "X=1\n")
    target = _write(tmp_path, ".env.prod", "X=1\n")
    report = build_report(base, [target])
    lines = report.summary_lines()
    assert "[OK]" in lines[1]


def test_summary_lines_diff_status(tmp_path):
    base = _write(tmp_path, ".env.base", "X=1\nY=2\n")
    target = _write(tmp_path, ".env.prod", "X=1\n")
    report = build_report(base, [target])
    lines = report.summary_lines()
    assert "[DIFF]" in lines[1]


def test_build_report_check_values_mismatch(tmp_path):
    base = _write(tmp_path, ".env.base", "KEY=foo\n")
    target = _write(tmp_path, ".env.prod", "KEY=bar\n")
    report = build_report(base, [target], check_values=True)
    assert report.any_differences
    assert "KEY" in report.results[target].mismatched
