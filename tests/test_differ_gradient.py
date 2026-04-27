"""Tests for envdiff.differ_gradient and envdiff.gradient_formatter."""
from __future__ import annotations

from pathlib import Path

import pytest

from envdiff.differ_gradient import build_gradient, GradientEntry
from envdiff.gradient_formatter import format_gradient_rich, format_gradient_summary


def _write(tmp_path: Path, name: str, content: str) -> str:
    p = tmp_path / name
    p.write_text(content)
    return str(p)


# ---------------------------------------------------------------------------
# build_gradient
# ---------------------------------------------------------------------------

def test_all_keys_present_in_result(tmp_path):
    a = _write(tmp_path, "a.env", "FOO=1\nBAR=x\n")
    b = _write(tmp_path, "b.env", "FOO=2\nBAR=x\n")
    result = build_gradient([a, b])
    keys = {e.key for e in result.entries}
    assert "FOO" in keys
    assert "BAR" in keys


def test_keys_sorted(tmp_path):
    a = _write(tmp_path, "a.env", "Z=1\nA=2\nM=3\n")
    result = build_gradient([a])
    assert [e.key for e in result.entries] == ["A", "M", "Z"]


def test_stable_key_has_zero_changes(tmp_path):
    a = _write(tmp_path, "a.env", "KEY=same\n")
    b = _write(tmp_path, "b.env", "KEY=same\n")
    result = build_gradient([a, b])
    entry = next(e for e in result.entries if e.key == "KEY")
    assert entry.change_count == 0
    assert entry.is_stable


def test_changed_value_increments_change_count(tmp_path):
    a = _write(tmp_path, "a.env", "KEY=v1\n")
    b = _write(tmp_path, "b.env", "KEY=v2\n")
    c = _write(tmp_path, "c.env", "KEY=v3\n")
    result = build_gradient([a, b, c])
    entry = next(e for e in result.entries if e.key == "KEY")
    assert entry.change_count == 2


def test_absent_key_marked(tmp_path):
    a = _write(tmp_path, "a.env", "FOO=1\n")
    b = _write(tmp_path, "b.env", "BAR=2\n")
    result = build_gradient([a, b])
    foo = next(e for e in result.entries if e.key == "FOO")
    assert foo.is_absent_in_some
    assert foo.values[1] is None


def test_first_and_last_value(tmp_path):
    a = _write(tmp_path, "a.env", "X=alpha\n")
    b = _write(tmp_path, "b.env", "X=beta\n")
    result = build_gradient([a, b])
    entry = next(e for e in result.entries if e.key == "X")
    assert entry.first_value == "alpha"
    assert entry.last_value == "beta"


def test_single_file_no_changes(tmp_path):
    a = _write(tmp_path, "a.env", "A=1\nB=2\n")
    result = build_gradient([a])
    assert all(e.change_count == 0 for e in result.entries)


def test_unstable_and_stable_split(tmp_path):
    a = _write(tmp_path, "a.env", "SAME=x\nDIFF=1\n")
    b = _write(tmp_path, "b.env", "SAME=x\nDIFF=2\n")
    result = build_gradient([a, b])
    assert len(result.stable_keys()) == 1
    assert len(result.unstable_keys()) == 1


# ---------------------------------------------------------------------------
# gradient_formatter
# ---------------------------------------------------------------------------

def test_rich_contains_header(tmp_path):
    a = _write(tmp_path, "a.env", "K=1\n")
    b = _write(tmp_path, "b.env", "K=2\n")
    result = build_gradient([a, b])
    out = format_gradient_rich(result)
    assert "Gradient report" in out


def test_rich_shows_unstable_key(tmp_path):
    a = _write(tmp_path, "a.env", "FOO=1\n")
    b = _write(tmp_path, "b.env", "FOO=2\n")
    result = build_gradient([a, b])
    out = format_gradient_rich(result)
    assert "FOO" in out
    assert "Unstable" in out


def test_rich_shows_values_when_flag_set(tmp_path):
    a = _write(tmp_path, "a.env", "FOO=hello\n")
    b = _write(tmp_path, "b.env", "FOO=world\n")
    result = build_gradient([a, b])
    out = format_gradient_rich(result, show_values=True)
    assert "hello" in out
    assert "world" in out


def test_summary_contains_counts(tmp_path):
    a = _write(tmp_path, "a.env", "A=1\nB=x\n")
    b = _write(tmp_path, "b.env", "A=2\nB=x\n")
    result = build_gradient([a, b])
    summary = format_gradient_summary(result)
    assert "1 unstable" in summary
    assert "1 stable" in summary


def test_empty_result_message(tmp_path):
    a = _write(tmp_path, "a.env", "")
    result = build_gradient([a])
    out = format_gradient_rich(result)
    assert "No keys" in out
