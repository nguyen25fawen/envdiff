"""Tests for envdiff.differ_watchlist."""
from __future__ import annotations

from pathlib import Path

import pytest

from envdiff.comparator import DiffResult
from envdiff.differ_watchlist import (
    WatchlistHit,
    WatchlistResult,
    apply_watchlist,
    load_watchlist,
)


def _diff(
    missing_in_second=None,
    missing_in_first=None,
    mismatched=None,
) -> DiffResult:
    return DiffResult(
        missing_in_second=list(missing_in_second or []),
        missing_in_first=list(missing_in_first or []),
        mismatched=list(mismatched or []),
    )


def _write(tmp_path: Path, content: str) -> Path:
    p = tmp_path / ".watchlist"
    p.write_text(content)
    return p


# --- load_watchlist ---

def test_load_watchlist_basic(tmp_path):
    p = _write(tmp_path, "SECRET_KEY\nDB_PASSWORD\n")
    patterns = load_watchlist(p)
    assert patterns == ["SECRET_KEY", "DB_PASSWORD"]


def test_load_watchlist_skips_comments(tmp_path):
    p = _write(tmp_path, "# comment\nSECRET_KEY\n")
    assert load_watchlist(p) == ["SECRET_KEY"]


def test_load_watchlist_skips_blank_lines(tmp_path):
    p = _write(tmp_path, "\nSECRET_KEY\n\n")
    assert load_watchlist(p) == ["SECRET_KEY"]


def test_load_watchlist_glob_pattern(tmp_path):
    p = _write(tmp_path, "*_KEY\n*_SECRET\n")
    patterns = load_watchlist(p)
    assert "*_KEY" in patterns
    assert "*_SECRET" in patterns


# --- apply_watchlist ---

def test_no_hits_when_no_patterns():
    diff = _diff(missing_in_second=["SECRET_KEY"])
    result = apply_watchlist(diff, [])
    assert result.is_empty()


def test_missing_in_second_hit():
    diff = _diff(missing_in_second=["SECRET_KEY"])
    result = apply_watchlist(diff, ["SECRET_KEY"])
    assert not result.is_empty()
    assert result.hits[0].kind == "missing_in_second"
    assert result.hits[0].key == "SECRET_KEY"


def test_missing_in_first_hit():
    diff = _diff(missing_in_first=["DB_PASSWORD"])
    result = apply_watchlist(diff, ["DB_PASSWORD"])
    assert result.hits[0].kind == "missing_in_first"


def test_mismatch_hit():
    diff = _diff(mismatched=["API_TOKEN"])
    result = apply_watchlist(diff, ["API_TOKEN"])
    assert result.hits[0].kind == "mismatch"


def test_glob_matches_wildcard():
    diff = _diff(missing_in_second=["AWS_SECRET_KEY", "SAFE_KEY"])
    result = apply_watchlist(diff, ["*SECRET*"])
    keys = [h.key for h in result.hits]
    assert "AWS_SECRET_KEY" in keys
    assert "SAFE_KEY" not in keys


def test_hits_sorted_by_key():
    diff = _diff(missing_in_second=["Z_KEY", "A_KEY"])
    result = apply_watchlist(diff, ["*_KEY"])
    assert [h.key for h in result.hits] == ["A_KEY", "Z_KEY"]


def test_by_kind_filter():
    diff = _diff(missing_in_second=["X"], mismatched=["Y"])
    result = apply_watchlist(diff, ["X", "Y"])
    assert len(result.by_kind("missing_in_second")) == 1
    assert len(result.by_kind("mismatch")) == 1
    assert len(result.by_kind("missing_in_first")) == 0
