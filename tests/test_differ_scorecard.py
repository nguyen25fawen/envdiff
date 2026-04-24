"""Tests for envdiff.differ_scorecard."""
import pytest

from envdiff.differ import EnvDiff
from envdiff.differ_scorecard import (
    ScorecardEntry,
    ScorecardResult,
    build_scorecard,
)


def _diff(
    base: dict,
    target: dict,
    mismatched: dict | None = None,
) -> EnvDiff:
    missing_in_target = [k for k in base if k not in target]
    missing_in_base = [k for k in target if k not in base]
    mm = mismatched or {}
    return EnvDiff(
        base=base,
        target=target,
        missing_in_target=missing_in_target,
        missing_in_base=missing_in_base,
        mismatched=mm,
    )


def test_build_scorecard_empty_list():
    result = build_scorecard([])
    assert result.is_empty
    assert result.overall_health == 100.0
    assert not result.any_issues


def test_build_scorecard_clean_pair():
    d = _diff({"A": "1", "B": "2"}, {"A": "1", "B": "2"})
    result = build_scorecard([d], labels=["prod"])
    assert len(result.entries) == 1
    entry = result.entries[0]
    assert entry.label == "prod"
    assert entry.total_keys == 2
    assert entry.total_issues == 0
    assert entry.health_pct == 100.0


def test_build_scorecard_missing_in_target():
    d = _diff({"A": "1", "B": "2"}, {"A": "1"})
    result = build_scorecard([d])
    entry = result.entries[0]
    assert entry.missing_in_target == 1
    assert entry.total_issues == 1
    assert entry.health_pct < 100.0


def test_build_scorecard_missing_in_base():
    d = _diff({"A": "1"}, {"A": "1", "B": "2"})
    result = build_scorecard([d])
    entry = result.entries[0]
    assert entry.missing_in_base == 1
    assert entry.total_issues == 1


def test_build_scorecard_mismatched():
    d = _diff({"A": "1"}, {"A": "2"}, mismatched={"A": ("1", "2")})
    result = build_scorecard([d])
    entry = result.entries[0]
    assert entry.mismatched == 1
    assert entry.total_issues == 1


def test_default_label_when_none_provided():
    d = _diff({"X": "1"}, {"X": "1"})
    result = build_scorecard([d])
    assert result.entries[0].label == "pair-1"


def test_overall_health_average_of_entries():
    d1 = _diff({"A": "1"}, {"A": "1"})          # 100%
    d2 = _diff({"A": "1", "B": "2"}, {"A": "1"})  # 50%
    result = build_scorecard([d1, d2])
    assert result.overall_health == 75.0


def test_any_issues_true_when_problems_exist():
    d = _diff({"A": "1", "B": "2"}, {"A": "1"})
    result = build_scorecard([d])
    assert result.any_issues


def test_health_pct_zero_keys_is_100():
    d = _diff({}, {})
    result = build_scorecard([d])
    assert result.entries[0].health_pct == 100.0
