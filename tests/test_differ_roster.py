"""Tests for envdiff.differ_roster."""
from __future__ import annotations

from pathlib import Path

import pytest

from envdiff.differ_roster import build_roster, RosterEntry, RosterResult


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _write(tmp_path: Path, name: str, content: str) -> Path:
    p = tmp_path / name
    p.write_text(content)
    return p


# ---------------------------------------------------------------------------
# tests
# ---------------------------------------------------------------------------

def test_all_keys_present_in_result(tmp_path):
    a = _write(tmp_path, "a.env", "FOO=1\nBAR=2\n")
    b = _write(tmp_path, "b.env", "FOO=1\nBAZ=3\n")
    result = build_roster([a, b])
    keys = {e.key for e in result.entries}
    assert keys == {"FOO", "BAR", "BAZ"}


def test_universal_key_present_in_all(tmp_path):
    a = _write(tmp_path, "a.env", "FOO=1\n")
    b = _write(tmp_path, "b.env", "FOO=2\n")
    result = build_roster([a, b])
    assert result.universal_keys()[0].key == "FOO"


def test_orphan_key_in_one_file(tmp_path):
    a = _write(tmp_path, "a.env", "FOO=1\nUNIQUE=x\n")
    b = _write(tmp_path, "b.env", "FOO=1\n")
    result = build_roster([a, b])
    orphans = {e.key for e in result.orphan_keys()}
    assert "UNIQUE" in orphans


def test_partial_key_not_universal_not_orphan(tmp_path):
    a = _write(tmp_path, "a.env", "K=1\n")
    b = _write(tmp_path, "b.env", "K=1\n")
    c = _write(tmp_path, "c.env", "OTHER=2\n")
    result = build_roster([a, b, c])
    partial = {e.key for e in result.partial_keys()}
    assert "K" in partial


def test_coverage_fraction(tmp_path):
    a = _write(tmp_path, "a.env", "FOO=1\n")
    b = _write(tmp_path, "b.env", "FOO=1\n")
    c = _write(tmp_path, "c.env", "BAR=2\n")
    result = build_roster([a, b, c])
    foo_entry = next(e for e in result.entries if e.key == "FOO")
    assert abs(foo_entry.coverage - 2 / 3) < 1e-9


def test_entries_sorted_alphabetically(tmp_path):
    a = _write(tmp_path, "a.env", "ZEBRA=1\nAPPLE=2\nMIDDLE=3\n")
    result = build_roster([a])
    keys = [e.key for e in result.entries]
    assert keys == sorted(keys)


def test_files_list_preserved(tmp_path):
    a = _write(tmp_path, "a.env", "X=1\n")
    b = _write(tmp_path, "b.env", "Y=2\n")
    result = build_roster([a, b])
    assert str(a) in result.files
    assert str(b) in result.files


def test_empty_files_produce_empty_result(tmp_path):
    a = _write(tmp_path, "a.env", "")
    b = _write(tmp_path, "b.env", "")
    result = build_roster([a, b])
    assert result.is_empty()


def test_single_file_all_keys_are_orphans(tmp_path):
    a = _write(tmp_path, "a.env", "FOO=1\nBAR=2\n")
    result = build_roster([a])
    assert all(e.is_orphan for e in result.entries)


def test_is_universal_false_when_absent(tmp_path):
    a = _write(tmp_path, "a.env", "FOO=1\n")
    b = _write(tmp_path, "b.env", "BAR=2\n")
    result = build_roster([a, b])
    for entry in result.entries:
        assert not entry.is_universal
