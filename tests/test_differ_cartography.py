"""Tests for envdiff.differ_cartography."""
from pathlib import Path

import pytest

from envdiff.differ_cartography import build_cartography, CartographyEntry


def _write(tmp_path: Path, name: str, content: str) -> str:
    p = tmp_path / name
    p.write_text(content)
    return str(p)


def test_all_keys_present_in_result(tmp_path):
    a = _write(tmp_path, "a.env", "FOO=1\nBAR=2\n")
    b = _write(tmp_path, "b.env", "FOO=1\nBAZ=3\n")
    result = build_cartography([a, b])
    keys = {e.key for e in result.entries}
    assert keys == {"FOO", "BAR", "BAZ"}


def test_keys_sorted(tmp_path):
    a = _write(tmp_path, "a.env", "ZEBRA=1\nAPPLE=2\n")
    result = build_cartography([a])
    assert [e.key for e in result.entries] == ["APPLE", "ZEBRA"]


def test_universal_key_present_in_all(tmp_path):
    a = _write(tmp_path, "a.env", "SHARED=x\n")
    b = _write(tmp_path, "b.env", "SHARED=x\n")
    result = build_cartography([a, b])
    shared = next(e for e in result.entries if e.key == "SHARED")
    assert shared.is_universal is True
    assert result.universal_keys() == [shared]


def test_orphan_key_in_one_file(tmp_path):
    a = _write(tmp_path, "a.env", "ONLY_A=1\n")
    b = _write(tmp_path, "b.env", "OTHER=2\n")
    result = build_cartography([a, b])
    orphans = {e.key for e in result.orphan_keys()}
    assert "ONLY_A" in orphans
    assert "OTHER" in orphans


def test_missing_from_populated(tmp_path):
    a = _write(tmp_path, "a.env", "FOO=1\n")
    b = _write(tmp_path, "b.env", "BAR=2\n")
    result = build_cartography([a, b])
    foo = next(e for e in result.entries if e.key == "FOO")
    assert b in foo.missing_from
    assert a not in foo.missing_from


def test_values_tracked_per_file(tmp_path):
    a = _write(tmp_path, "a.env", "KEY=hello\n")
    b = _write(tmp_path, "b.env", "KEY=world\n")
    result = build_cartography([a, b])
    entry = next(e for e in result.entries if e.key == "KEY")
    assert entry.values[a] == "hello"
    assert entry.values[b] == "world"


def test_uniform_when_values_equal(tmp_path):
    a = _write(tmp_path, "a.env", "PORT=8080\n")
    b = _write(tmp_path, "b.env", "PORT=8080\n")
    result = build_cartography([a, b])
    entry = next(e for e in result.entries if e.key == "PORT")
    assert entry.is_uniform is True


def test_not_uniform_when_values_differ(tmp_path):
    a = _write(tmp_path, "a.env", "PORT=8080\n")
    b = _write(tmp_path, "b.env", "PORT=9090\n")
    result = build_cartography([a, b])
    entry = next(e for e in result.entries if e.key == "PORT")
    assert entry.is_uniform is False
    assert entry in result.conflicted_keys()


def test_empty_files_yield_empty_result(tmp_path):
    a = _write(tmp_path, "a.env", "")
    b = _write(tmp_path, "b.env", "")
    result = build_cartography([a, b])
    assert result.is_empty() is True


def test_files_list_preserved(tmp_path):
    a = _write(tmp_path, "a.env", "X=1\n")
    b = _write(tmp_path, "b.env", "Y=2\n")
    result = build_cartography([a, b])
    assert result.files == [a, b]
