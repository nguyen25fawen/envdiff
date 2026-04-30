"""Tests for envdiff.differ_frequency."""
from __future__ import annotations

from pathlib import Path

import pytest

from envdiff.differ_frequency import build_frequency, FrequencyEntry, FrequencyResult


def _write(tmp_path: Path, name: str, content: str) -> str:
    p = tmp_path / name
    p.write_text(content)
    return str(p)


def test_universal_key_present_in_all(tmp_path):
    a = _write(tmp_path, "a.env", "KEY=1\n")
    b = _write(tmp_path, "b.env", "KEY=2\n")
    result = build_frequency([a, b])
    entry = next(e for e in result.entries if e.key == "KEY")
    assert entry.is_universal
    assert entry.count == 2
    assert entry.frequency == 1.0


def test_rare_key_in_one_of_three(tmp_path):
    a = _write(tmp_path, "a.env", "KEY=1\nRAREKEY=x\n")
    b = _write(tmp_path, "b.env", "KEY=2\n")
    c = _write(tmp_path, "c.env", "KEY=3\n")
    result = build_frequency([a, b, c])
    entry = next(e for e in result.entries if e.key == "RAREKEY")
    assert entry.is_rare
    assert entry.count == 1
    assert pytest.approx(entry.frequency) == 1 / 3


def test_keys_sorted_alphabetically(tmp_path):
    a = _write(tmp_path, "a.env", "ZEBRA=1\nAPPLE=2\n")
    result = build_frequency([a])
    keys = [e.key for e in result.entries]
    assert keys == sorted(keys)


def test_total_files_recorded(tmp_path):
    a = _write(tmp_path, "a.env", "X=1\n")
    b = _write(tmp_path, "b.env", "X=1\n")
    c = _write(tmp_path, "c.env", "X=1\n")
    result = build_frequency([a, b, c])
    assert result.total_files == 3


def test_files_list_contains_path(tmp_path):
    a = _write(tmp_path, "a.env", "FOO=bar\n")
    result = build_frequency([a])
    entry = result.entries[0]
    assert a in entry.files


def test_empty_file_produces_empty_result(tmp_path):
    a = _write(tmp_path, "a.env", "")
    result = build_frequency([a])
    assert result.is_empty()


def test_universal_keys_helper(tmp_path):
    a = _write(tmp_path, "a.env", "SHARED=1\nONLY_A=x\n")
    b = _write(tmp_path, "b.env", "SHARED=2\n")
    result = build_frequency([a, b])
    universal = [e.key for e in result.universal_keys()]
    assert "SHARED" in universal
    assert "ONLY_A" not in universal


def test_rare_keys_helper(tmp_path):
    a = _write(tmp_path, "a.env", "SHARED=1\nRARE=x\n")
    b = _write(tmp_path, "b.env", "SHARED=2\n")
    c = _write(tmp_path, "c.env", "SHARED=3\n")
    result = build_frequency([a, b, c])
    rare = [e.key for e in result.rare_keys()]
    assert "RARE" in rare
    assert "SHARED" not in rare
