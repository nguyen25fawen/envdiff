"""Tests for envdiff.differ_matrix."""
from __future__ import annotations

import pathlib
import pytest

from envdiff.differ_matrix import (
    build_matrix,
    matrix_missing_pairs,
    matrix_value_conflicts,
)


def _write(tmp_path: pathlib.Path, name: str, content: str) -> str:
    p = tmp_path / name
    p.write_text(content)
    return str(p)


def test_build_matrix_keys_sorted(tmp_path):
    a = _write(tmp_path, "a.env", "Z=1\nA=2\n")
    b = _write(tmp_path, "b.env", "A=2\nM=3\n")
    result = build_matrix([a, b])
    assert result.keys == ["A", "M", "Z"]


def test_build_matrix_files_preserved(tmp_path):
    a = _write(tmp_path, "a.env", "KEY=1\n")
    b = _write(tmp_path, "b.env", "KEY=1\n")
    result = build_matrix([a, b])
    assert result.files == [a, b]


def test_cell_present_when_key_exists(tmp_path):
    a = _write(tmp_path, "a.env", "FOO=bar\n")
    b = _write(tmp_path, "b.env", "FOO=baz\n")
    result = build_matrix([a, b])
    assert result.rows["FOO"][0].present is True
    assert result.rows["FOO"][1].present is True


def test_cell_absent_when_key_missing(tmp_path):
    a = _write(tmp_path, "a.env", "FOO=bar\n")
    b = _write(tmp_path, "b.env", "OTHER=x\n")
    result = build_matrix([a, b])
    assert result.rows["FOO"][1].present is False
    assert result.rows["FOO"][1].value is None


def test_matrix_missing_pairs_returns_correct_entries(tmp_path):
    a = _write(tmp_path, "a.env", "FOO=1\nBAR=2\n")
    b = _write(tmp_path, "b.env", "FOO=1\n")
    result = build_matrix([a, b])
    missing = matrix_missing_pairs(result)
    assert ("BAR", b) in missing
    assert len(missing) == 1


def test_matrix_missing_pairs_empty_when_all_present(tmp_path):
    a = _write(tmp_path, "a.env", "KEY=1\n")
    b = _write(tmp_path, "b.env", "KEY=2\n")
    result = build_matrix([a, b])
    assert matrix_missing_pairs(result) == []


def test_matrix_value_conflicts_detected(tmp_path):
    a = _write(tmp_path, "a.env", "DB=postgres\n")
    b = _write(tmp_path, "b.env", "DB=mysql\n")
    result = build_matrix([a, b])
    conflicts = matrix_value_conflicts(result)
    assert len(conflicts) == 1
    key, vals = conflicts[0]
    assert key == "DB"
    assert "postgres" in vals
    assert "mysql" in vals


def test_matrix_no_conflicts_when_values_equal(tmp_path):
    a = _write(tmp_path, "a.env", "PORT=8080\n")
    b = _write(tmp_path, "b.env", "PORT=8080\n")
    result = build_matrix([a, b])
    assert matrix_value_conflicts(result) == []


def test_build_matrix_single_file(tmp_path):
    a = _write(tmp_path, "a.env", "X=1\nY=2\n")
    result = build_matrix([a])
    assert result.keys == ["X", "Y"]
    assert all(cell.present for cell in result.rows["X"])
