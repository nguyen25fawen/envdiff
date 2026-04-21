"""Tests for envdiff.differ_pivot."""
from __future__ import annotations

import pathlib
import pytest

from envdiff.differ_pivot import pivot_files, PivotRow, PivotCell


def _write(tmp_path: pathlib.Path, name: str, content: str) -> str:
    p = tmp_path / name
    p.write_text(content)
    return str(p)


def test_pivot_all_keys_present(tmp_path):
    a = _write(tmp_path, "a.env", "FOO=1\nBAR=2\n")
    b = _write(tmp_path, "b.env", "FOO=1\nBAR=2\n")
    result = pivot_files([a, b])
    assert {r.key for r in result.rows} == {"FOO", "BAR"}


def test_pivot_keys_sorted(tmp_path):
    a = _write(tmp_path, "a.env", "ZEBRA=z\nAPPLE=a\n")
    b = _write(tmp_path, "b.env", "ZEBRA=z\nAPPLE=a\n")
    result = pivot_files([a, b])
    assert [r.key for r in result.rows] == ["APPLE", "ZEBRA"]


def test_pivot_uniform_row_when_values_equal(tmp_path):
    a = _write(tmp_path, "a.env", "FOO=same\n")
    b = _write(tmp_path, "b.env", "FOO=same\n")
    result = pivot_files([a, b])
    assert result.rows[0].is_uniform is True


def test_pivot_not_uniform_when_values_differ(tmp_path):
    a = _write(tmp_path, "a.env", "FOO=hello\n")
    b = _write(tmp_path, "b.env", "FOO=world\n")
    result = pivot_files([a, b])
    assert result.rows[0].is_uniform is False


def test_pivot_absent_cell_when_key_missing(tmp_path):
    a = _write(tmp_path, "a.env", "FOO=1\n")
    b = _write(tmp_path, "b.env", "BAR=2\n")
    result = pivot_files([a, b])
    foo_row = next(r for r in result.rows if r.key == "FOO")
    assert foo_row.cells[0].value == "1"
    assert foo_row.cells[1].value is None


def test_pivot_is_universal_false_when_key_absent(tmp_path):
    a = _write(tmp_path, "a.env", "FOO=1\n")
    b = _write(tmp_path, "b.env", "BAR=2\n")
    result = pivot_files([a, b])
    foo_row = next(r for r in result.rows if r.key == "FOO")
    assert foo_row.is_universal is False


def test_pivot_conflicted_rows(tmp_path):
    a = _write(tmp_path, "a.env", "FOO=1\nBAR=same\n")
    b = _write(tmp_path, "b.env", "FOO=2\nBAR=same\n")
    result = pivot_files([a, b])
    assert len(result.conflicted_rows()) == 1
    assert result.conflicted_rows()[0].key == "FOO"


def test_pivot_missing_rows(tmp_path):
    a = _write(tmp_path, "a.env", "FOO=1\n")
    b = _write(tmp_path, "b.env", "BAR=2\n")
    result = pivot_files([a, b])
    missing = {r.key for r in result.missing_rows()}
    assert missing == {"FOO", "BAR"}


def test_pivot_three_files(tmp_path):
    a = _write(tmp_path, "a.env", "KEY=v1\n")
    b = _write(tmp_path, "b.env", "KEY=v2\n")
    c = _write(tmp_path, "c.env", "KEY=v3\n")
    result = pivot_files([a, b, c])
    assert len(result.files) == 3
    assert len(result.rows[0].cells) == 3


def test_pivot_empty_files(tmp_path):
    a = _write(tmp_path, "a.env", "")
    b = _write(tmp_path, "b.env", "")
    result = pivot_files([a, b])
    assert result.rows == []
