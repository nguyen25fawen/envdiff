"""Tests for envdiff.lens_formatter."""
from __future__ import annotations

from envdiff.comparator import DiffResult
from envdiff.differ_lens import LensResult, LensRule
from envdiff.lens_formatter import format_lens_rich, format_lens_summary


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _rule(name: str = "test", patterns=None) -> LensRule:
    return LensRule(name=name, patterns=patterns or ["TEST_*"])


def _result(
    lens: LensRule = None,
    missing_second=None,
    missing_first=None,
    mismatched=None,
    total: int = 5,
) -> LensResult:
    lens = lens or _rule()
    focused = DiffResult(
        missing_in_second=missing_second or [],
        missing_in_first=missing_first or [],
        mismatched=mismatched or {},
    )
    matched = len(focused.missing_in_second) + len(focused.missing_in_first) + len(focused.mismatched)
    return LensResult(lens=lens, focused=focused, total_keys=total, matched_keys=matched)


# ---------------------------------------------------------------------------
# format_lens_rich
# ---------------------------------------------------------------------------

def test_rich_contains_lens_name():
    out = format_lens_rich(_result(lens=_rule(name="auth")))
    assert "auth" in out


def test_rich_shows_pattern():
    out = format_lens_rich(_result(lens=_rule(patterns=["SECRET_*"])))
    assert "SECRET_*" in out


def test_rich_shows_missing_in_second():
    out = format_lens_rich(_result(missing_second=["TEST_HOST"]))
    assert "TEST_HOST" in out


def test_rich_shows_missing_in_first():
    out = format_lens_rich(_result(missing_first=["TEST_PORT"]))
    assert "TEST_PORT" in out


def test_rich_shows_mismatch_key():
    out = format_lens_rich(_result(mismatched={"TEST_KEY": ("a", "b")}))
    assert "TEST_KEY" in out


def test_rich_hides_values_by_default():
    out = format_lens_rich(_result(mismatched={"TEST_KEY": ("secret", "other")}))
    assert "secret" not in out


def test_rich_shows_values_when_flag_set():
    out = format_lens_rich(
        _result(mismatched={"TEST_KEY": ("secret", "other")}),
        show_values=True,
    )
    assert "secret" in out
    assert "other" in out


def test_rich_no_issues_message_when_clean():
    out = format_lens_rich(_result())
    assert "No issues" in out


# ---------------------------------------------------------------------------
# format_lens_summary
# ---------------------------------------------------------------------------

def test_summary_contains_lens_name():
    out = format_lens_summary(_result(lens=_rule(name="infra")))
    assert "infra" in out


def test_summary_clean_when_no_issues():
    out = format_lens_summary(_result())
    assert "clean" in out


def test_summary_shows_issue_count_when_present():
    out = format_lens_summary(_result(missing_second=["TEST_A", "TEST_B"]))
    assert "2" in out
