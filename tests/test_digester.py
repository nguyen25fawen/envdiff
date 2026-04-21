"""Tests for envdiff.digester."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from envdiff.digester import (
    DigestEntry,
    DigestResult,
    _checksum,
    digest_file,
    digest_many,
    load_digest,
    save_digest,
)


def _write(tmp_path: Path, name: str, content: str) -> Path:
    p = tmp_path / name
    p.write_text(content)
    return p


def test_checksum_deterministic():
    env = {"B": "2", "A": "1"}
    assert _checksum(env) == _checksum(env)


def test_checksum_order_independent():
    assert _checksum({"A": "1", "B": "2"}) == _checksum({"B": "2", "A": "1"})


def test_checksum_differs_for_different_values():
    assert _checksum({"A": "1"}) != _checksum({"A": "2"})


def test_digest_file_key_count(tmp_path):
    p = _write(tmp_path, "a.env", "X=1\nY=2\n")
    entry = digest_file(p)
    assert entry.key_count == 2


def test_digest_file_checksum_stable(tmp_path):
    p = _write(tmp_path, "a.env", "X=1\n")
    assert digest_file(p).checksum == digest_file(p).checksum


def test_digest_many_no_conflicts_when_identical(tmp_path):
    a = _write(tmp_path, "a.env", "X=1\n")
    b = _write(tmp_path, "b.env", "X=1\n")
    result = digest_many([a, b])
    assert result.conflicts == []


def test_digest_many_conflict_detected(tmp_path):
    a = _write(tmp_path, "a.env", "X=1\n")
    b = _write(tmp_path, "b.env", "X=2\n")
    result = digest_many([a, b])
    assert str(b) in result.conflicts


def test_digest_many_entries_count(tmp_path):
    files = [_write(tmp_path, f"{i}.env", f"K={i}\n") for i in range(3)]
    result = digest_many(files)
    assert len(result.entries) == 3


def test_save_and_load_roundtrip(tmp_path):
    a = _write(tmp_path, "a.env", "A=1\n")
    b = _write(tmp_path, "b.env", "A=1\n")
    result = digest_many([a, b])
    dest = tmp_path / "digest.json"
    save_digest(result, dest)
    loaded = load_digest(dest)
    assert len(loaded.entries) == len(result.entries)
    assert loaded.entries[0].checksum == result.entries[0].checksum


def test_save_creates_parent_dirs(tmp_path):
    a = _write(tmp_path, "a.env", "A=1\n")
    result = digest_many([a])
    dest = tmp_path / "sub" / "nested" / "digest.json"
    save_digest(result, dest)
    assert dest.exists()


def test_load_detects_conflicts_after_roundtrip(tmp_path):
    a = _write(tmp_path, "a.env", "A=1\n")
    b = _write(tmp_path, "b.env", "A=99\n")
    result = digest_many([a, b])
    dest = tmp_path / "digest.json"
    save_digest(result, dest)
    loaded = load_digest(dest)
    assert len(loaded.conflicts) == 1
