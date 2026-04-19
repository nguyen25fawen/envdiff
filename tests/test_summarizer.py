"""Tests for envdiff.summarizer and envdiff.summary_formatter."""
import os
import pytest
from envdiff.summarizer import summarize
from envdiff.summary_formatter import format_summary


def _write(tmp_path, name, content):
    p = tmp_path / name
    p.write_text(content)
    return str(p)


def test_total_keys(tmp_path):
    a = _write(tmp_path, "a.env", "FOO=1\nBAR=2\n")
    b = _write(tmp_path, "b.env", "FOO=1\nBAZ=3\n")
    s = summarize([a, b])
    assert s.total_keys() == 3


def test_universal_keys(tmp_path):
    a = _write(tmp_path, "a.env", "FOO=1\nBAR=2\n")
    b = _write(tmp_path, "b.env", "FOO=1\nBAR=2\n")
    s = summarize([a, b])
    assert s.universal_keys() == ["BAR", "FOO"]


def test_partial_keys(tmp_path):
    a = _write(tmp_path, "a.env", "FOO=1\nBAR=2\n")
    b = _write(tmp_path, "b.env", "FOO=1\n")
    s = summarize([a, b])
    assert "BAR" in s.partial_keys()


def test_unique_values_counted(tmp_path):
    a = _write(tmp_path, "a.env", "FOO=hello\n")
    b = _write(tmp_path, "b.env", "FOO=world\n")
    s = summarize([a, b])
    assert s.stats["FOO"].unique_values == 2


def test_same_values_unique_count_one(tmp_path):
    a = _write(tmp_path, "a.env", "FOO=same\n")
    b = _write(tmp_path, "b.env", "FOO=same\n")
    s = summarize([a, b])
    assert s.stats["FOO"].unique_values == 1


def test_empty_value_detected(tmp_path):
    a = _write(tmp_path, "a.env", "FOO=\n")
    b = _write(tmp_path, "b.env", "FOO=val\n")
    s = summarize([a, b])
    assert s.stats["FOO"].has_empty is True


def test_format_summary_contains_header(tmp_path):
    a = _write(tmp_path, "a.env", "FOO=1\n")
    b = _write(tmp_path, "b.env", "FOO=1\n")
    s = summarize([a, b])
    out = format_summary(s, color=False)
    assert "Env Summary" in out
    assert "2 file(s)" in out


def test_format_summary_partial_key_shown(tmp_path):
    a = _write(tmp_path, "a.env", "FOO=1\nBAR=2\n")
    b = _write(tmp_path, "b.env", "FOO=1\n")
    s = summarize([a, b])
    out = format_summary(s, color=False)
    assert "BAR" in out
    assert "missing in" in out


def test_format_summary_values_differ_note(tmp_path):
    a = _write(tmp_path, "a.env", "FOO=a\n")
    b = _write(tmp_path, "b.env", "FOO=b\n")
    s = summarize([a, b])
    out = format_summary(s, color=False)
    assert "values differ" in out
