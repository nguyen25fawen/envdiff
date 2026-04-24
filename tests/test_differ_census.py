"""Tests for envdiff.differ_census."""
from __future__ import annotations

from pathlib import Path

import pytest

from envdiff.differ_census import build_census, CensusEntry


def _write(tmp_path: Path, name: str, content: str) -> Path:
    p = tmp_path / name
    p.write_text(content)
    return p


def test_universal_key_present_in_all(tmp_path):
    a = _write(tmp_path, "a.env", "SHARED=1\n")
    b = _write(tmp_path, "b.env", "SHARED=2\n")
    result = build_census([a, b])
    universal = result.universal_keys()
    assert any(e.key == "SHARED" for e in universal)


def test_orphan_key_in_one_file(tmp_path):
    a = _write(tmp_path, "a.env", "ONLY_A=1\n")
    b = _write(tmp_path, "b.env", "OTHER=2\n")
    result = build_census([a, b])
    orphans = result.orphan_keys()
    keys = {e.key for e in orphans}
    assert "ONLY_A" in keys
    assert "OTHER" in keys


def test_partial_key_in_subset(tmp_path):
    a = _write(tmp_path, "a.env", "SHARED=1\nPARTIAL=x\n")
    b = _write(tmp_path, "b.env", "SHARED=2\n")
    c = _write(tmp_path, "c.env", "SHARED=3\nPARTIAL=y\n")
    result = build_census([a, b, c])
    partial = result.partial_keys()
    assert any(e.key == "PARTIAL" for e in partial)


def test_coverage_is_fraction(tmp_path):
    a = _write(tmp_path, "a.env", "K=1\n")
    b = _write(tmp_path, "b.env", "K=2\n")
    c = _write(tmp_path, "c.env", "OTHER=3\n")
    result = build_census([a, b, c])
    entry = next(e for e in result.entries if e.key == "K")
    assert abs(entry.coverage - 2 / 3) < 1e-9


def test_all_keys_union(tmp_path):
    a = _write(tmp_path, "a.env", "A=1\nB=2\n")
    b = _write(tmp_path, "b.env", "B=3\nC=4\n")
    result = build_census([a, b])
    keys = {e.key for e in result.entries}
    assert keys == {"A", "B", "C"}


def test_empty_files_produce_empty_result(tmp_path):
    a = _write(tmp_path, "a.env", "")
    b = _write(tmp_path, "b.env", "")
    result = build_census([a, b])
    assert result.is_empty()


def test_single_file_all_keys_are_orphans(tmp_path):
    a = _write(tmp_path, "a.env", "X=1\nY=2\n")
    result = build_census([a])
    assert all(e.is_orphan for e in result.entries)
    assert all(e.is_universal for e in result.entries)


def test_absent_from_populated(tmp_path):
    a = _write(tmp_path, "a.env", "ONLY=1\n")
    b = _write(tmp_path, "b.env", "OTHER=2\n")
    result = build_census([a, b])
    entry = next(e for e in result.entries if e.key == "ONLY")
    assert str(b) in entry.absent_from
    assert str(a) in entry.present_in
