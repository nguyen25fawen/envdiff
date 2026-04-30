"""Tests for envdiff.differ_entropy."""
from __future__ import annotations

import math
import pathlib

import pytest

from envdiff.differ_entropy import (
    EntropyEntry,
    EntropyResult,
    _shannon,
    build_entropy,
)


def _write(tmp_path: pathlib.Path, name: str, content: str) -> str:
    p = tmp_path / name
    p.write_text(content)
    return str(p)


def test_shannon_uniform_returns_zero():
    assert _shannon(["x", "x", "x"]) == pytest.approx(0.0)


def test_shannon_two_equal_halves():
    result = _shannon(["a", "b"])
    assert result == pytest.approx(1.0)


def test_shannon_empty_returns_zero():
    assert _shannon([]) == pytest.approx(0.0)


def test_shannon_four_distinct_values():
    result = _shannon(["a", "b", "c", "d"])
    assert result == pytest.approx(2.0)


def test_build_entropy_all_keys_present(tmp_path):
    f1 = _write(tmp_path, "a.env", "FOO=1\nBAR=x\n")
    f2 = _write(tmp_path, "b.env", "FOO=2\nBAR=x\n")
    result = build_entropy([f1, f2])
    keys = [e.key for e in result.entries]
    assert "FOO" in keys
    assert "BAR" in keys


def test_build_entropy_keys_sorted(tmp_path):
    f1 = _write(tmp_path, "a.env", "ZEBRA=1\nAPPLE=2\n")
    result = build_entropy([f1])
    assert [e.key for e in result.entries] == ["APPLE", "ZEBRA"]


def test_build_entropy_uniform_key(tmp_path):
    f1 = _write(tmp_path, "a.env", "KEY=same\n")
    f2 = _write(tmp_path, "b.env", "KEY=same\n")
    result = build_entropy([f1, f2])
    entry = next(e for e in result.entries if e.key == "KEY")
    assert entry.is_uniform
    assert entry.entropy == pytest.approx(0.0)


def test_build_entropy_chaotic_key(tmp_path):
    f1 = _write(tmp_path, "a.env", "KEY=alpha\n")
    f2 = _write(tmp_path, "b.env", "KEY=beta\n")
    result = build_entropy([f1, f2])
    entry = next(e for e in result.entries if e.key == "KEY")
    assert entry.is_chaotic
    assert entry.entropy == pytest.approx(1.0)


def test_build_entropy_total_files(tmp_path):
    f1 = _write(tmp_path, "a.env", "A=1\n")
    f2 = _write(tmp_path, "b.env", "A=2\n")
    f3 = _write(tmp_path, "c.env", "A=3\n")
    result = build_entropy([f1, f2, f3])
    assert result.total_files == 3


def test_build_entropy_partial_key(tmp_path):
    """Key present in only some files — total_count reflects presence."""
    f1 = _write(tmp_path, "a.env", "ONLY=here\n")
    f2 = _write(tmp_path, "b.env", "OTHER=val\n")
    result = build_entropy([f1, f2])
    entry = next(e for e in result.entries if e.key == "ONLY")
    assert entry.total_count == 1


def test_uniform_keys_helper(tmp_path):
    f1 = _write(tmp_path, "a.env", "U=same\nV=one\n")
    f2 = _write(tmp_path, "b.env", "U=same\nV=two\n")
    result = build_entropy([f1, f2])
    uniform = [e.key for e in result.uniform_keys()]
    assert "U" in uniform
    assert "V" not in uniform


def test_is_empty_when_no_files(tmp_path):
    f1 = _write(tmp_path, "empty.env", "")
    result = build_entropy([f1])
    assert result.is_empty()
