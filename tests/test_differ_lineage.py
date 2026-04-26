"""Tests for envdiff.differ_lineage."""
import pytest
from pathlib import Path

from envdiff.differ_lineage import build_lineage, LineageEntry, LineageResult


def _write(tmp_path: Path, name: str, content: str) -> str:
    p = tmp_path / name
    p.write_text(content)
    return str(p)


def test_all_keys_present_in_result(tmp_path):
    a = _write(tmp_path, "a.env", "FOO=1\nBAR=2\n")
    b = _write(tmp_path, "b.env", "FOO=1\nBAZ=3\n")
    result = build_lineage([a, b])
    keys = {e.key for e in result.entries}
    assert keys == {"FOO", "BAR", "BAZ"}


def test_keys_sorted(tmp_path):
    a = _write(tmp_path, "a.env", "ZEBRA=z\nAPPLE=a\n")
    result = build_lineage([a])
    assert [e.key for e in result.entries] == ["APPLE", "ZEBRA"]


def test_first_seen_in_correct(tmp_path):
    a = _write(tmp_path, "a.env", "NEW=1\n")
    b = _write(tmp_path, "b.env", "NEW=1\nOLD=2\n")
    result = build_lineage([a, b])
    by_key = {e.key: e for e in result.entries}
    assert by_key["NEW"].first_seen_in == a
    assert by_key["OLD"].first_seen_in == b


def test_last_seen_in_correct(tmp_path):
    a = _write(tmp_path, "a.env", "FOO=1\n")
    b = _write(tmp_path, "b.env", "FOO=2\n")
    c = _write(tmp_path, "c.env", "BAR=3\n")
    result = build_lineage([a, b, c])
    by_key = {e.key: e for e in result.entries}
    assert by_key["FOO"].last_seen_in == b
    assert by_key["BAR"].last_seen_in == c


def test_changed_true_when_value_differs(tmp_path):
    a = _write(tmp_path, "a.env", "FOO=old\n")
    b = _write(tmp_path, "b.env", "FOO=new\n")
    result = build_lineage([a, b])
    assert result.entries[0].changed is True


def test_changed_false_when_value_same(tmp_path):
    a = _write(tmp_path, "a.env", "FOO=same\n")
    b = _write(tmp_path, "b.env", "FOO=same\n")
    result = build_lineage([a, b])
    assert result.entries[0].changed is False


def test_orphan_key_single_source(tmp_path):
    a = _write(tmp_path, "a.env", "ONLY_HERE=1\n")
    b = _write(tmp_path, "b.env", "OTHER=2\n")
    result = build_lineage([a, b])
    orphans = {e.key for e in result.orphan_keys()}
    assert "ONLY_HERE" in orphans
    assert "OTHER" in orphans


def test_stable_keys_excludes_changed(tmp_path):
    a = _write(tmp_path, "a.env", "STABLE=x\nMUTABLE=1\n")
    b = _write(tmp_path, "b.env", "STABLE=x\nMUTABLE=2\n")
    result = build_lineage([a, b])
    stable = {e.key for e in result.stable_keys()}
    assert "STABLE" in stable
    assert "MUTABLE" not in stable


def test_source_count_correct(tmp_path):
    a = _write(tmp_path, "a.env", "FOO=1\n")
    b = _write(tmp_path, "b.env", "FOO=2\n")
    c = _write(tmp_path, "c.env", "FOO=3\n")
    result = build_lineage([a, b, c])
    assert result.entries[0].source_count == 3


def test_value_at_returns_correct(tmp_path):
    a = _write(tmp_path, "a.env", "FOO=hello\n")
    b = _write(tmp_path, "b.env", "FOO=world\n")
    result = build_lineage([a, b])
    entry = result.entries[0]
    assert entry.value_at(a) == "hello"
    assert entry.value_at(b) == "world"


def test_is_empty_for_no_keys(tmp_path):
    a = _write(tmp_path, "a.env", "")
    result = build_lineage([a])
    assert result.is_empty()


def test_files_preserved_in_result(tmp_path):
    a = _write(tmp_path, "a.env", "X=1\n")
    b = _write(tmp_path, "b.env", "Y=2\n")
    result = build_lineage([a, b])
    assert result.files == [a, b]
