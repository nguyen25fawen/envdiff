"""Tests for envdiff.watchlist_formatter."""
from __future__ import annotations

from envdiff.comparator import DiffResult
from envdiff.differ_watchlist import WatchlistHit, WatchlistResult, apply_watchlist
from envdiff.watchlist_formatter import format_watchlist_rich, format_watchlist_summary


def _result(hits=None, patterns=None) -> WatchlistResult:
    return WatchlistResult(
        patterns=patterns or ["SECRET_KEY"],
        hits=hits or [],
    )


def _hit(key="SECRET_KEY", pattern="SECRET_KEY", kind="missing_in_second") -> WatchlistHit:
    return WatchlistHit(key=key, pattern=pattern, kind=kind)


def test_empty_result_shows_clean_message():
    out = format_watchlist_rich(_result())
    assert "No watchlist keys affected" in out


def test_rich_contains_header():
    out = format_watchlist_rich(_result())
    assert "Watchlist Report" in out


def test_rich_shows_pattern_count():
    out = format_watchlist_rich(_result(patterns=["A", "B"]))
    assert "Patterns: 2" in out


def test_rich_shows_hit_key():
    out = format_watchlist_rich(_result(hits=[_hit(key="MY_SECRET")]))
    assert "MY_SECRET" in out


def test_rich_shows_missing_in_second_label():
    out = format_watchlist_rich(_result(hits=[_hit(kind="missing_in_second")]))
    assert "MISSING" in out


def test_rich_shows_mismatch_label():
    out = format_watchlist_rich(_result(hits=[_hit(kind="mismatch")]))
    assert "MISMATCH" in out


def test_rich_shows_pattern_in_hit():
    out = format_watchlist_rich(_result(hits=[_hit(pattern="*SECRET*")]))
    assert "*SECRET*" in out


def test_summary_no_hits():
    out = format_watchlist_summary(_result())
    assert "no hits" in out


def test_summary_with_hits():
    out = format_watchlist_summary(_result(hits=[_hit(), _hit(key="X", kind="mismatch")]))
    assert "2 hit" in out


def test_summary_lists_kinds():
    hits = [
        _hit(kind="missing_in_second"),
        _hit(key="B", kind="mismatch"),
    ]
    out = format_watchlist_summary(_result(hits=hits))
    assert "missing_in_second" in out
    assert "mismatch" in out
