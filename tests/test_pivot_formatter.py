"""Tests for envdiff.pivot_formatter."""
from __future__ import annotations

import pathlib
import pytest

from envdiff.differ_pivot import pivot_files, PivotResult, PivotRow, PivotCell
from envdiff.pivot_formatter import format_pivot_rich, format_pivot_summary


def _write(tmp_path: pathlib.Path, name: str, content: str) -> str:
    p = tmp_path / name
    p.write_text(content)
    return str(p)


def _result(tmp_path, a_content: str, b_content: str) -> PivotResult:
    a = _write(tmp_path, "a.env", a_content)
    b = _write(tmp_path, "b.env", b_content)
    return pivot_files([a, b])


def test_rich_contains_header(tmp_path):
    r = _result(tmp_path, "FOO=1\n", "FOO=1\n")
    out = format_pivot_rich(r)
    assert "Pivot view" in out


def test_rich_shows_key_name(tmp_path):
    r = _result(tmp_path, "MY_KEY=x\n", "MY_KEY=x\n")
    out = format_pivot_rich(r)
    assert "MY_KEY" in out


def test_rich_masks_values_by_default(tmp_path):
    r = _result(tmp_path, "SECRET=abc\n", "SECRET=abc\n")
    out = format_pivot_rich(r)
    assert "abc" not in out
    assert "***" in out


def test_rich_shows_values_when_flag_set(tmp_path):
    r = _result(tmp_path, "TOKEN=myval\n", "TOKEN=myval\n")
    out = format_pivot_rich(r, show_values=True)
    assert "myval" in out


def test_rich_shows_absent_for_missing_key(tmp_path):
    r = _result(tmp_path, "FOO=1\n", "BAR=2\n")
    out = format_pivot_rich(r)
    assert "absent" in out


def test_rich_conflicts_only_hides_uniform_rows(tmp_path):
    r = _result(tmp_path, "FOO=1\nBAR=same\n", "FOO=2\nBAR=same\n")
    out = format_pivot_rich(r, only_conflicts=True)
    assert "FOO" in out
    assert "BAR" not in out


def test_rich_no_conflicts_message_when_empty(tmp_path):
    r = _result(tmp_path, "FOO=1\n", "FOO=1\n")
    out = format_pivot_rich(r, only_conflicts=True)
    assert "No conflicts" in out


def test_summary_no_issues(tmp_path):
    r = _result(tmp_path, "FOO=1\n", "FOO=1\n")
    s = format_pivot_summary(r)
    assert "no conflicts" in s.lower()


def test_summary_shows_conflict_count(tmp_path):
    r = _result(tmp_path, "FOO=1\n", "FOO=2\n")
    s = format_pivot_summary(r)
    assert "conflict" in s.lower()


def test_summary_shows_absent_count(tmp_path):
    r = _result(tmp_path, "FOO=1\n", "BAR=2\n")
    s = format_pivot_summary(r)
    assert "absent" in s.lower()
