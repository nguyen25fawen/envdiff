"""Tests for envdiff.merger."""
from __future__ import annotations

from pathlib import Path

import pytest

from envdiff.merger import merge_envs, render_merged, write_merged


def _write(tmp_path: Path, name: str, content: str) -> Path:
    p = tmp_path / name
    p.write_text(content, encoding="utf-8")
    return p


def test_merge_single_file(tmp_path):
    p = _write(tmp_path, "a.env", "FOO=bar\nBAZ=qux\n")
    result = merge_envs([p])
    assert result == {"FOO": "bar", "BAZ": "qux"}


def test_merge_first_value_wins(tmp_path):
    a = _write(tmp_path, "a.env", "FOO=first\n")
    b = _write(tmp_path, "b.env", "FOO=second\n")
    result = merge_envs([a, b])
    assert result["FOO"] == "first"


def test_merge_union_of_keys(tmp_path):
    a = _write(tmp_path, "a.env", "FOO=1\n")
    b = _write(tmp_path, "b.env", "BAR=2\n")
    result = merge_envs([a, b])
    assert set(result.keys()) == {"FOO", "BAR"}


def test_fill_missing_uses_placeholder(tmp_path):
    a = _write(tmp_path, "a.env", "FOO=1\nBAR=2\n")
    b = _write(tmp_path, "b.env", "FOO=1\nBAZ=3\n")
    result = merge_envs([a, b], placeholder="CHANGEME")
    assert result["BAZ"] == "CHANGEME"


def test_fill_missing_false_keeps_original(tmp_path):
    a = _write(tmp_path, "a.env", "FOO=1\n")
    b = _write(tmp_path, "b.env", "BAR=2\n")
    result = merge_envs([a, b], fill_missing=False)
    # Still unions keys but values come from first-seen source
    assert "FOO" in result and "BAR" in result


def test_render_merged_format():
    merged = {"A": "1", "B": "hello"}
    output = render_merged(merged)
    assert "A=1\n" in output
    assert "B=hello\n" in output


def test_render_merged_empty():
    assert render_merged({}) == ""


def test_write_merged_creates_file(tmp_path):
    out = tmp_path / "out" / "merged.env"
    write_merged({"X": "y"}, out)
    assert out.exists()
    assert "X=y" in out.read_text()


def test_write_merged_creates_parents(tmp_path):
    out = tmp_path / "deep" / "nested" / "dir" / ".env"
    write_merged({"K": "v"}, out)
    assert out.exists()
