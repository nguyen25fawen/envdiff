"""Tests for envdiff.formatter."""

from envdiff.comparator import DiffResult
from envdiff.formatter import format_diff


def _make_result(**kwargs) -> DiffResult:
    return DiffResult(**kwargs)


def test_no_differences_message():
    result = _make_result()
    output = format_diff(result, use_color=False)
    assert "No differences found" in output


def test_missing_in_second_shown():
    result = _make_result(missing_in_second=["DEBUG", "LOG_LEVEL"])
    output = format_diff(result, use_color=False)
    assert "DEBUG" in output
    assert "LOG_LEVEL" in output


def test_missing_in_first_shown():
    result = _make_result(missing_in_first=["SECRET_KEY"])
    output = format_diff(result, first_label="dev", second_label="prod", use_color=False)
    assert "SECRET_KEY" in output
    assert "prod" in output


def test_value_mismatch_masked_by_default():
    result = _make_result(value_mismatches={"DB_PASS": ("hunter2", "s3cr3t")})
    output = format_diff(result, use_color=False, mask_values=True)
    assert "hunter2" not in output
    assert "s3cr3t" not in output
    assert "DB_PASS" in output


def test_value_mismatch_unmasked():
    result = _make_result(value_mismatches={"DB_PASS": ("hunter2", "s3cr3t")})
    output = format_diff(result, use_color=False, mask_values=False)
    assert "hunter2" in output
    assert "s3cr3t" in output


def test_color_codes_present_when_enabled():
    result = _make_result(missing_in_second=["FOO"])
    output = format_diff(result, use_color=True)
    assert "\033[" in output


def test_color_codes_absent_when_disabled():
    result = _make_result(missing_in_second=["FOO"])
    output = format_diff(result, use_color=False)
    assert "\033[" not in output
