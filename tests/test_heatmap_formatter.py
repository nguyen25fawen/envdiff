"""Tests for envdiff.heatmap_formatter."""
from __future__ import annotations

from envdiff.differ_heatmap import HeatmapEntry, HeatmapResult, build_heatmap
from envdiff.heatmap_formatter import format_heatmap_rich, format_heatmap_summary
from envdiff.differ import EnvDiff


def _result(*entries: HeatmapEntry, pairs: int = 1) -> HeatmapResult:
    return HeatmapResult(entries=list(entries), total_pairs=pairs)


def _entry(key: str, miss: int = 0, mismatch: int = 0) -> HeatmapEntry:
    return HeatmapEntry(key=key, miss_count=miss, mismatch_count=mismatch)


def test_empty_result_shows_no_differences():
    result = _result(pairs=0)
    out = format_heatmap_rich(result)
    assert "No differences" in out


def test_header_contains_pair_count():
    result = _result(_entry("FOO", miss=1), pairs=3)
    out = format_heatmap_rich(result)
    assert "3" in out


def test_key_appears_in_output():
    result = _result(_entry("DB_HOST", miss=2))
    out = format_heatmap_rich(result)
    assert "DB_HOST" in out


def test_hot_label_present_for_hot_entry():
    result = _result(_entry("SECRET", miss=5))
    out = format_heatmap_rich(result)
    assert "HOT" in out


def test_cool_label_present_for_cool_entry():
    result = _result(_entry("MINOR", miss=1))
    out = format_heatmap_rich(result)
    assert "COOL" in out


def test_show_counts_includes_miss_label():
    result = _result(_entry("X", miss=3, mismatch=1))
    out = format_heatmap_rich(result, show_counts=True)
    assert "miss=3" in out
    assert "mismatch=1" in out


def test_hide_counts_omits_miss_label():
    result = _result(_entry("X", miss=3))
    out = format_heatmap_rich(result, show_counts=False)
    assert "miss=" not in out
    assert "total=3" in out


def test_summary_contains_key_count():
    result = _result(_entry("A", miss=1), _entry("B", mismatch=5), pairs=2)
    summary = format_heatmap_summary(result)
    assert "2 key(s)" in summary
    assert "2 pair(s)" in summary


def test_summary_counts_hot_entries():
    result = _result(_entry("A", miss=5), _entry("B", miss=1), pairs=5)
    summary = format_heatmap_summary(result)
    assert "1 hot" in summary
