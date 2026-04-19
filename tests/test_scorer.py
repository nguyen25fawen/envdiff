"""Tests for envdiff.scorer."""
import pytest
from envdiff.comparator import DiffResult
from envdiff.reporter import ComparisonReport
from envdiff.scorer import score_report, format_score, EnvScore


def _report(*pairs):
    """Build a ComparisonReport from (label, DiffResult) pairs."""
    r = ComparisonReport(base="base.env", diffs={})
    for label, diff in pairs:
        r.diffs[label] = diff
    return r


def _diff(missing_second=(), missing_first=(), mismatched=()):
    return DiffResult(
        missing_in_second=list(missing_second),
        missing_in_first=list(missing_first),
        mismatched_values=dict(mismatched),
    )


def test_perfect_score_no_issues():
    report = _report(("prod", _diff()))
    s = score_report(report, ["A", "B", "C"])
    assert s.score == 100.0
    assert s.grade == "A"
    assert s.missing_count == 0
    assert s.mismatch_count == 0


def test_missing_keys_reduce_score():
    report = _report(("prod", _diff(missing_second=["X", "Y", "Z"])))
    s = score_report(report, ["X", "Y", "Z"])
    assert s.score < 100.0
    assert s.missing_count == 3


def test_mismatch_reduces_score():
    report = _report(("prod", _diff(mismatched=[("KEY", ("a", "b"))])))
    s = score_report(report, ["KEY"])
    assert s.score < 100.0
    assert s.mismatch_count == 1


def test_empty_base_keys_returns_perfect():
    report = _report(("prod", _diff(missing_second=["X"])))
    s = score_report(report, [])
    assert s.score == 100.0
    assert s.grade == "A"


def test_grade_f_on_all_missing():
    keys = [str(i) for i in range(20)]
    report = _report(("prod", _diff(missing_second=keys)))
    s = score_report(report, keys)
    assert s.grade == "F"


def test_total_keys_recorded():
    report = _report(("prod", _diff()))
    s = score_report(report, ["A", "B"])
    assert s.total_keys == 2


def test_format_score_contains_grade():
    es = EnvScore(total_keys=5, missing_count=1, mismatch_count=0, score=88.0, grade="B")
    out = format_score(es)
    assert "88.0" in out
    assert "[B]" in out
    assert "Missing" in out
