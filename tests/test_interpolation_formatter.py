"""Tests for envdiff.interpolation_formatter."""
from envdiff.interpolator import InterpolationResult
from envdiff.interpolation_formatter import (
    format_interpolation_result,
    format_interpolation_summary,
)


def _result(**kwargs) -> InterpolationResult:
    r = InterpolationResult()
    for k, v in kwargs.items():
        setattr(r, k, v)
    return r


def test_clean_result_message():
    r = InterpolationResult(resolved={"A": "1"}, unresolved={}, references={})
    out = format_interpolation_result(r)
    assert "resolved" in out.lower()
    assert "unresolved" not in out.lower() or "0" in out


def test_unresolved_key_shown():
    r = InterpolationResult(
        resolved={"URL": "http://${HOST}/"},
        unresolved={"URL": ["HOST"]},
        references={"URL": ["HOST"]},
    )
    out = format_interpolation_result(r)
    assert "URL" in out
    assert "HOST" in out


def test_show_resolved_flag():
    r = InterpolationResult(
        resolved={"URL": "http://localhost/"},
        unresolved={},
        references={"URL": ["HOST"]},
    )
    out = format_interpolation_result(r, show_resolved=True)
    assert "URL" in out
    assert "localhost" in out


def test_summary_contains_counts():
    r = InterpolationResult(
        resolved={"A": "x", "B": "${MISSING}"},
        unresolved={"B": ["MISSING"]},
        references={"B": ["MISSING"]},
    )
    summary = format_interpolation_summary(r)
    assert "1" in summary  # 1 interpolated total


def test_summary_all_resolved():
    r = InterpolationResult(
        resolved={"A": "hello"},
        unresolved={},
        references={"A": ["BASE"]},
    )
    summary = format_interpolation_summary(r)
    assert "0" in summary or "unresolved" in summary.lower()


def test_format_result_empty():
    """An empty InterpolationResult should produce output without raising."""
    r = InterpolationResult(resolved={}, unresolved={}, references={})
    out = format_interpolation_result(r)
    assert isinstance(out, str)
    assert len(out) >= 0


def test_format_result_multiple_unresolved_refs():
    """Keys with multiple unresolved references should each appear in the output."""
    r = InterpolationResult(
        resolved={"DSN": "${USER}:${PASS}@${HOST}/db"},
        unresolved={"DSN": ["USER", "PASS", "HOST"]},
        references={"DSN": ["USER", "PASS", "HOST"]},
    )
    out = format_interpolation_result(r)
    assert "DSN" in out
    assert "USER" in out
    assert "PASS" in out
    assert "HOST" in out
