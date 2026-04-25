"""Tests for envdiff.differ_archiver and envdiff.archive_formatter."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from envdiff.differ_archiver import (
    ArchiveEntry,
    ArchiveResult,
    build_archive,
    load_archive,
    save_archive,
    _checksum,
)
from envdiff.archive_formatter import format_archive_rich, format_archive_summary


def _write(tmp_path: Path, name: str, content: str) -> Path:
    p = tmp_path / name
    p.write_text(content)
    return p


# ---------------------------------------------------------------------------
# _checksum
# ---------------------------------------------------------------------------

def test_checksum_deterministic():
    env = {"A": "1", "B": "2"}
    assert _checksum(env) == _checksum(env)


def test_checksum_order_independent():
    assert _checksum({"A": "1", "B": "2"}) == _checksum({"B": "2", "A": "1"})


def test_checksum_differs_for_different_values():
    assert _checksum({"A": "1"}) != _checksum({"A": "2"})


# ---------------------------------------------------------------------------
# build_archive
# ---------------------------------------------------------------------------

def test_build_archive_key_count(tmp_path):
    p = _write(tmp_path, "a.env", "X=1\nY=2\n")
    result = build_archive([p])
    assert result.entries[0].key_count == 2


def test_build_archive_keys_sorted(tmp_path):
    p = _write(tmp_path, "a.env", "Z=3\nA=1\nM=2\n")
    result = build_archive([p])
    assert result.entries[0].keys == ["A", "M", "Z"]


def test_build_archive_total_files(tmp_path):
    p1 = _write(tmp_path, "a.env", "A=1\n")
    p2 = _write(tmp_path, "b.env", "B=2\n")
    result = build_archive([p1, p2])
    assert result.total_files == 2


def test_build_archive_total_keys(tmp_path):
    p1 = _write(tmp_path, "a.env", "A=1\nB=2\n")
    p2 = _write(tmp_path, "b.env", "C=3\n")
    result = build_archive([p1, p2])
    assert result.total_keys == 3


def test_build_archive_custom_label(tmp_path):
    p = _write(tmp_path, "a.env", "A=1\n")
    result = build_archive([p], label="release-1.0")
    assert result.label == "release-1.0"


# ---------------------------------------------------------------------------
# save_archive / load_archive
# ---------------------------------------------------------------------------

def test_save_and_load_roundtrip(tmp_path):
    p = _write(tmp_path, "a.env", "KEY=val\n")
    result = build_archive([p], label="test-label")
    dest = tmp_path / "archives" / "snap.json"
    save_archive(result, dest)
    loaded = load_archive(dest)
    assert loaded.label == "test-label"
    assert loaded.total_files == 1
    assert loaded.entries[0].key_count == 1


def test_save_creates_parent_dirs(tmp_path):
    p = _write(tmp_path, "a.env", "A=1\n")
    result = build_archive([p])
    dest = tmp_path / "deep" / "nested" / "archive.json"
    save_archive(result, dest)
    assert dest.exists()


# ---------------------------------------------------------------------------
# formatters
# ---------------------------------------------------------------------------

def test_format_archive_rich_contains_label(tmp_path):
    p = _write(tmp_path, "a.env", "A=1\n")
    result = build_archive([p], label="my-snap")
    output = format_archive_rich(result, color=False)
    assert "my-snap" in output


def test_format_archive_rich_shows_path(tmp_path):
    p = _write(tmp_path, "env.env", "A=1\n")
    result = build_archive([p])
    output = format_archive_rich(result, color=False)
    assert "env.env" in output


def test_format_archive_summary_contains_file_count(tmp_path):
    p1 = _write(tmp_path, "a.env", "A=1\n")
    p2 = _write(tmp_path, "b.env", "B=2\n")
    result = build_archive([p1, p2])
    summary = format_archive_summary(result)
    assert "2 file(s)" in summary


def test_format_archive_summary_contains_key_count(tmp_path):
    p = _write(tmp_path, "a.env", "A=1\nB=2\nC=3\n")
    result = build_archive([p])
    summary = format_archive_summary(result)
    assert "3 total key(s)" in summary
