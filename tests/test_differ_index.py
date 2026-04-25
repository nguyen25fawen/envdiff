"""Tests for envdiff.differ_index."""
from __future__ import annotations

from pathlib import Path

import pytest

from envdiff.differ_index import build_index, IndexEntry, IndexResult


def _write(tmp_path: Path, name: str, content: str) -> str:
    p = tmp_path / name
    p.write_text(content)
    return str(p)


def test_build_index_single_file(tmp_path):
    f = _write(tmp_path, "a.env", "KEY=hello\n")
    result = build_index([f])
    assert "hello" in result.entries
    assert result.entries["hello"].count == 1


def test_build_index_shared_value(tmp_path):
    f1 = _write(tmp_path, "a.env", "FOO=shared\n")
    f2 = _write(tmp_path, "b.env", "BAR=shared\n")
    result = build_index([f1, f2])
    entry = result.entries["shared"]
    assert entry.count == 2
    assert entry.is_shared()


def test_build_index_unique_value(tmp_path):
    f1 = _write(tmp_path, "a.env", "FOO=unique\n")
    f2 = _write(tmp_path, "b.env", "BAR=other\n")
    result = build_index([f1, f2])
    assert not result.entries["unique"].is_shared()
    assert not result.entries["other"].is_shared()


def test_empty_values_excluded(tmp_path):
    f = _write(tmp_path, "a.env", "EMPTY=\nKEY=val\n")
    result = build_index([f])
    assert "" not in result.entries
    assert "val" in result.entries


def test_shared_values_sorted_by_count_desc(tmp_path):
    f1 = _write(tmp_path, "a.env", "A=x\nB=x\nC=x\n")
    f2 = _write(tmp_path, "b.env", "D=y\nE=y\n")
    result = build_index([f1, f2])
    shared = result.shared_values()
    assert shared[0].value == "x"
    assert shared[0].count == 3
    assert shared[1].value == "y"
    assert shared[1].count == 2


def test_files_list_preserved(tmp_path):
    f1 = _write(tmp_path, "a.env", "K=v\n")
    f2 = _write(tmp_path, "b.env", "K=v\n")
    result = build_index([f1, f2])
    assert f1 in result.files
    assert f2 in result.files


def test_is_empty_on_no_values(tmp_path):
    f = _write(tmp_path, "empty.env", "EMPTY=\n")
    result = build_index([f])
    assert result.is_empty()


def test_entry_keys_and_files(tmp_path):
    f1 = _write(tmp_path, "a.env", "FOO=same\n")
    f2 = _write(tmp_path, "b.env", "BAR=same\n")
    result = build_index([f1, f2])
    entry = result.entries["same"]
    assert "FOO" in entry.keys
    assert "BAR" in entry.keys
    assert f1 in entry.files
    assert f2 in entry.files


def test_unique_values_list(tmp_path):
    f1 = _write(tmp_path, "a.env", "A=solo\nB=duo\n")
    f2 = _write(tmp_path, "b.env", "C=duo\n")
    result = build_index([f1, f2])
    unique_vals = [e.value for e in result.unique_values()]
    assert "solo" in unique_vals
    assert "duo" not in unique_vals
