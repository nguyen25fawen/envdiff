"""Tests for envdiff.baseline_formatter."""
import pytest
from pathlib import Path

from envdiff.baseline import compare_against_base
from envdiff.baseline_formatter import format_baseline_result, format_baseline_summary


def _write(tmp_path: Path, name: str, content: str) -> str:
    p = tmp_path / name
    p.write_text(content)
    return str(p)


def test_format_contains_base_path(tmp_path):
    base = _write(tmp_path, "base.env", "FOO=1\n")
    target = _write(tmp_path, "t.env", "FOO=1\n")
    result = compare_against_base(base, [target])
    output = format_baseline_result(result)
    assert "base.env" in output


def test_format_contains_target_path(tmp_path):
    base = _write(tmp_path, "base.env", "FOO=1\n")
    target = _write(tmp_path, "t.env", "FOO=1\n")
    result = compare_against_base(base, [target])
    output = format_baseline_result(result)
    assert "t.env" in output


def test_format_shows_missing_key(tmp_path):
    base = _write(tmp_path, "base.env", "FOO=1\nBAR=2\n")
    target = _write(tmp_path, "t.env", "FOO=1\n")
    result = compare_against_base(base, [target])
    output = format_baseline_result(result)
    assert "BAR" in output


def test_summary_shows_total_targets(tmp_path):
    base = _write(tmp_path, "base.env", "A=1\n")
    t1 = _write(tmp_path, "t1.env", "A=1\n")
    t2 = _write(tmp_path, "t2.env", "A=1\n")
    result = compare_against_base(base, [t1, t2])
    summary = format_baseline_summary(result)
    assert "2" in summary


def test_summary_shows_clean_count(tmp_path):
    base = _write(tmp_path, "base.env", "A=1\n")
    t1 = _write(tmp_path, "t1.env", "A=1\n")
    result = compare_against_base(base, [t1])
    summary = format_baseline_summary(result)
    assert "Clean" in summary


def test_summary_shows_issues_count(tmp_path):
    base = _write(tmp_path, "base.env", "A=1\nB=2\n")
    t1 = _write(tmp_path, "t1.env", "A=1\n")
    result = compare_against_base(base, [t1])
    summary = format_baseline_summary(result)
    assert "With issues" in summary


def test_format_empty_targets(tmp_path):
    base = _write(tmp_path, "base.env", "A=1\n")
    result = compare_against_base(base, [])
    output = format_baseline_result(result)
    assert "base.env" in output
