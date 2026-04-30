"""Tests for envdiff.velocity_formatter."""
from __future__ import annotations

from pathlib import Path

from envdiff.differ_velocity import build_velocity
from envdiff.velocity_formatter import format_velocity_rich, format_velocity_summary


def _write(tmp_path: Path, name: str, content: str) -> str:
    p = tmp_path / name
    p.write_text(content)
    return str(p)


def _result(tmp_path):
    a = _write(tmp_path, "a.env", "STABLE=x\nVOL=1\nMOD=a\n")
    b = _write(tmp_path, "b.env", "STABLE=x\nVOL=2\nMOD=b\n")
    c = _write(tmp_path, "c.env", "STABLE=x\nVOL=3\nMOD=b\n")
    return build_velocity([a, b, c])


def test_rich_contains_header(tmp_path):
    out = format_velocity_rich(_result(tmp_path))
    assert "Velocity report" in out
    assert "3 files" in out


def test_rich_shows_key_name(tmp_path):
    out = format_velocity_rich(_result(tmp_path))
    assert "STABLE" in out
    assert "VOL" in out


def test_rich_shows_change_count(tmp_path):
    out = format_velocity_rich(_result(tmp_path))
    # VOL changes twice across 3 files
    assert "2" in out


def test_rich_show_values_flag(tmp_path):
    out = format_velocity_rich(_result(tmp_path), show_values=True)
    assert "[0]" in out
    assert "[1]" in out


def test_empty_result_shows_message(tmp_path):
    a = _write(tmp_path, "a.env", "")
    b = _write(tmp_path, "b.env", "")
    result = build_velocity([a, b])
    out = format_velocity_rich(result)
    assert "No keys found" in out


def test_summary_contains_counts(tmp_path):
    out = format_velocity_summary(_result(tmp_path))
    assert "stable" in out
    assert "volatile" in out
    assert "moderate" in out


def test_summary_contains_file_count(tmp_path):
    out = format_velocity_summary(_result(tmp_path))
    assert "3 files" in out
