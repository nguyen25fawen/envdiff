"""Tests for envdiff.differ_overlap and envdiff.overlap_formatter."""
from __future__ import annotations

from pathlib import Path

import pytest

from envdiff.differ_overlap import compute_overlap, OverlapResult
from envdiff.overlap_formatter import format_overlap_rich, format_overlap_summary


def _write(tmp_path: Path, name: str, content: str) -> str:
    p = tmp_path / name
    p.write_text(content)
    return str(p)


# ---------------------------------------------------------------------------
# compute_overlap
# ---------------------------------------------------------------------------

def test_universal_key_present_in_all(tmp_path):
    a = _write(tmp_path, "a.env", "SHARED=1\nONLY_A=x\n")
    b = _write(tmp_path, "b.env", "SHARED=2\nONLY_B=y\n")
    result = compute_overlap([a, b])
    assert "SHARED" in result.universal_keys


def test_exclusive_key_in_one_file(tmp_path):
    a = _write(tmp_path, "a.env", "SHARED=1\nONLY_A=x\n")
    b = _write(tmp_path, "b.env", "SHARED=2\n")
    result = compute_overlap([a, b])
    assert "ONLY_A" in result.exclusive_keys
    assert result.exclusive_keys["ONLY_A"] == a


def test_partial_key_in_subset(tmp_path):
    a = _write(tmp_path, "a.env", "K=1\nP=x\n")
    b = _write(tmp_path, "b.env", "K=2\nP=y\n")
    c = _write(tmp_path, "c.env", "K=3\n")
    result = compute_overlap([a, b, c])
    assert "P" in result.partial_keys
    assert "P" not in result.universal_keys
    assert "P" not in result.exclusive_keys


def test_all_keys_union(tmp_path):
    a = _write(tmp_path, "a.env", "X=1\n")
    b = _write(tmp_path, "b.env", "Y=2\n")
    result = compute_overlap([a, b])
    assert result.all_keys == frozenset({"X", "Y"})


def test_coverage_full(tmp_path):
    a = _write(tmp_path, "a.env", "K=1\n")
    b = _write(tmp_path, "b.env", "K=2\n")
    result = compute_overlap([a, b])
    assert result.coverage("K") == 1.0


def test_coverage_half(tmp_path):
    a = _write(tmp_path, "a.env", "K=1\n")
    b = _write(tmp_path, "b.env", "OTHER=2\n")
    result = compute_overlap([a, b])
    assert result.coverage("K") == 0.5


def test_empty_files_list():
    result = OverlapResult(files=[], all_keys=frozenset(), key_presence={})
    assert result.universal_keys == frozenset()
    assert result.coverage("ANY") == 0.0


# ---------------------------------------------------------------------------
# overlap_formatter
# ---------------------------------------------------------------------------

def test_format_rich_contains_universal_header(tmp_path):
    a = _write(tmp_path, "a.env", "SHARED=1\n")
    b = _write(tmp_path, "b.env", "SHARED=2\n")
    result = compute_overlap([a, b])
    output = format_overlap_rich(result)
    assert "Universal" in output
    assert "SHARED" in output


def test_format_rich_contains_exclusive(tmp_path):
    a = _write(tmp_path, "a.env", "ONLY_A=1\n")
    b = _write(tmp_path, "b.env", "ONLY_B=2\n")
    result = compute_overlap([a, b])
    output = format_overlap_rich(result)
    assert "Exclusive" in output


def test_format_summary_counts(tmp_path):
    a = _write(tmp_path, "a.env", "SHARED=1\nONLY_A=x\n")
    b = _write(tmp_path, "b.env", "SHARED=2\nONLY_B=y\n")
    result = compute_overlap([a, b])
    summary = format_overlap_summary(result)
    assert "3 total" in summary
    assert "1" in summary  # universal count


def test_format_rich_show_coverage(tmp_path):
    a = _write(tmp_path, "a.env", "K=1\n")
    b = _write(tmp_path, "b.env", "K=2\n")
    result = compute_overlap([a, b])
    output = format_overlap_rich(result, show_coverage=True)
    assert "%" in output
