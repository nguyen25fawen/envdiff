"""Tests for differ_stats and stats_formatter."""
import pytest
from envdiff.differ import EnvDiff
from envdiff.differ_stats import compute_stats, DiffStats
from envdiff.stats_formatter import format_stats_rich, format_stats_summary


def _diff(missing_target=(), missing_base=(), mismatched=()):
    return EnvDiff(
        missing_in_target=list(missing_target),
        missing_in_base=list(missing_base),
        mismatched=list(mismatched),
    )


def test_empty_list_returns_zero_stats():
    s = compute_stats([])
    assert s.total_pairs == 0
    assert s.total_issues == 0


def test_single_clean_diff():
    s = compute_stats([_diff()])
    assert s.total_pairs == 1
    assert s.total_issues == 0


def test_missing_in_target_counted():
    s = compute_stats([_diff(missing_target=["A", "B"])])
    assert s.total_missing_in_target == 2


def test_missing_in_base_counted():
    s = compute_stats([_diff(missing_base=["X"])])
    assert s.total_missing_in_base == 1


def test_mismatched_counted():
    s = compute_stats([_diff(mismatched=["PORT"])])
    assert s.total_mismatched == 1


def test_keys_always_missing_across_all_pairs():
    d1 = _diff(missing_target=["DB_URL", "SECRET"])
    d2 = _diff(missing_target=["DB_URL"])
    s = compute_stats([d1, d2])
    assert "DB_URL" in s.keys_always_missing
    assert "SECRET" not in s.keys_always_missing


def test_keys_always_mismatched_across_all_pairs():
    d1 = _diff(mismatched=["PORT"])
    d2 = _diff(mismatched=["PORT"])
    s = compute_stats([d1, d2])
    assert "PORT" in s.keys_always_mismatched


def test_keys_not_always_mismatched_excluded():
    d1 = _diff(mismatched=["PORT"])
    d2 = _diff(mismatched=[])
    s = compute_stats([d1, d2])
    assert "PORT" not in s.keys_always_mismatched


def test_format_stats_rich_contains_header():
    s = DiffStats(total_pairs=2, total_missing_in_target=1)
    out = format_stats_rich(s)
    assert "Diff Statistics" in out
    assert "2" in out


def test_format_stats_summary_clean():
    s = DiffStats(total_pairs=1)
    out = format_stats_summary(s)
    assert "clean" in out.lower()


def test_format_stats_summary_with_issues():
    s = DiffStats(total_pairs=2, total_missing_in_target=3, total_mismatched=1)
    out = format_stats_summary(s)
    assert "missing-in-target" in out
    assert "mismatched" in out


def test_format_rich_shows_always_missing():
    s = DiffStats(total_pairs=1, keys_always_missing=["DB_URL"])
    out = format_stats_rich(s)
    assert "DB_URL" in out
