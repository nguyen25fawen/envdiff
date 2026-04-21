"""Tests for envdiff.differ_heatmap."""
from __future__ import annotations

import pytest
from envdiff.differ_heatmap import build_heatmap, HeatmapEntry, HeatmapResult
from envdiff.differ import EnvDiff


def _diff(
    missing_in_target: list[str] | None = None,
    missing_in_base: list[str] | None = None,
    mismatched: list[str] | None = None,
) -> EnvDiff:
    return EnvDiff(
        missing_in_target=missing_in_target or [],
        missing_in_base=missing_in_base or [],
        mismatched=mismatched or [],
    )


def test_empty_diffs_returns_empty_result():
    result = build_heatmap([])
    assert result.is_empty()
    assert result.total_pairs == 0


def test_single_diff_missing_in_target():
    result = build_heatmap([_diff(missing_in_target=["FOO"])])
    assert result.total_pairs == 1
    keys = [e.key for e in result.entries]
    assert "FOO" in keys


def test_miss_count_accumulated():
    diffs = [
        _diff(missing_in_target=["DB_HOST"]),
        _diff(missing_in_target=["DB_HOST"]),
        _diff(missing_in_target=["DB_HOST"]),
    ]
    result = build_heatmap(diffs)
    entry = next(e for e in result.entries if e.key == "DB_HOST")
    assert entry.miss_count == 3
    assert entry.mismatch_count == 0
    assert entry.total == 3


def test_mismatch_count_accumulated():
    diffs = [_diff(mismatched=["API_KEY"]), _diff(mismatched=["API_KEY"])]
    result = build_heatmap(diffs)
    entry = next(e for e in result.entries if e.key == "API_KEY")
    assert entry.mismatch_count == 2


def test_heat_levels():
    e_cool = HeatmapEntry(key="A", miss_count=1)
    e_warm = HeatmapEntry(key="B", miss_count=2)
    e_hot = HeatmapEntry(key="C", miss_count=5)
    assert e_cool.heat == "cool"
    assert e_warm.heat == "warm"
    assert e_hot.heat == "hot"


def test_hottest_returns_top_n():
    diffs = [
        _diff(missing_in_target=["A", "B", "C"]),
        _diff(missing_in_target=["A", "B"]),
        _diff(missing_in_target=["A"]),
    ]
    result = build_heatmap(diffs)
    top2 = result.hottest(2)
    assert len(top2) == 2
    assert top2[0].key == "A"  # highest count


def test_entries_sorted_alphabetically_before_hottest():
    diffs = [_diff(missing_in_target=["Z", "A", "M"])]
    result = build_heatmap(diffs)
    keys = [e.key for e in result.entries]
    assert keys == sorted(keys)


def test_total_pairs_counted():
    diffs = [_diff(), _diff(), _diff()]
    result = build_heatmap(diffs)
    assert result.total_pairs == 3
