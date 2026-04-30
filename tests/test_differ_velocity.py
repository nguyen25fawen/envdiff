"""Tests for envdiff.differ_velocity."""
from __future__ import annotations

import os
from pathlib import Path

import pytest

from envdiff.differ_velocity import build_velocity, VelocityEntry, VelocityResult


def _write(tmp_path: Path, name: str, content: str) -> str:
    p = tmp_path / name
    p.write_text(content)
    return str(p)


def test_all_keys_present_in_result(tmp_path):
    a = _write(tmp_path, "a.env", "FOO=1\nBAR=x\n")
    b = _write(tmp_path, "b.env", "FOO=2\nBAZ=y\n")
    result = build_velocity([a, b])
    keys = {e.key for e in result.entries}
    assert keys == {"FOO", "BAR", "BAZ"}


def test_keys_sorted_alphabetically(tmp_path):
    a = _write(tmp_path, "a.env", "ZZZ=1\nAAA=2\n")
    b = _write(tmp_path, "b.env", "ZZZ=9\nAAA=2\n")
    result = build_velocity([a, b])
    assert [e.key for e in result.entries] == ["AAA", "ZZZ"]


def test_stable_key_has_zero_changes(tmp_path):
    a = _write(tmp_path, "a.env", "KEY=same\n")
    b = _write(tmp_path, "b.env", "KEY=same\n")
    c = _write(tmp_path, "c.env", "KEY=same\n")
    result = build_velocity([a, b, c])
    entry = result.by_key("KEY")
    assert entry is not None
    assert entry.change_count == 0
    assert entry.is_stable


def test_changed_value_increments_change_count(tmp_path):
    a = _write(tmp_path, "a.env", "KEY=v1\n")
    b = _write(tmp_path, "b.env", "KEY=v2\n")
    c = _write(tmp_path, "c.env", "KEY=v3\n")
    result = build_velocity([a, b, c])
    entry = result.by_key("KEY")
    assert entry.change_count == 2
    assert entry.is_volatile


def test_absent_key_tracked_as_none(tmp_path):
    a = _write(tmp_path, "a.env", "ONLY=here\n")
    b = _write(tmp_path, "b.env", "OTHER=there\n")
    result = build_velocity([a, b])
    entry = result.by_key("ONLY")
    assert entry.values == ["here", None]


def test_stable_and_volatile_lists(tmp_path):
    a = _write(tmp_path, "a.env", "STABLE=x\nVOL=1\n")
    b = _write(tmp_path, "b.env", "STABLE=x\nVOL=2\n")
    c = _write(tmp_path, "c.env", "STABLE=x\nVOL=3\n")
    result = build_velocity([a, b, c])
    assert "STABLE" in result.stable_keys()
    assert "VOL" in result.volatile_keys()


def test_is_empty_for_empty_files(tmp_path):
    a = _write(tmp_path, "a.env", "")
    b = _write(tmp_path, "b.env", "")
    result = build_velocity([a, b])
    assert result.is_empty


def test_first_and_last_seen(tmp_path):
    a = _write(tmp_path, "a.env", "")
    b = _write(tmp_path, "b.env", "LATE=1\n")
    c = _write(tmp_path, "c.env", "LATE=2\n")
    result = build_velocity([a, b, c])
    entry = result.by_key("LATE")
    assert entry.first_seen == 1
    assert entry.last_seen == 2


def test_files_stored_in_result(tmp_path):
    a = _write(tmp_path, "a.env", "X=1\n")
    b = _write(tmp_path, "b.env", "X=1\n")
    result = build_velocity([a, b])
    assert len(result.files) == 2
