"""Tests for envdiff.radar_formatter."""
from __future__ import annotations

from pathlib import Path

from envdiff.differ import diff_pair
from envdiff.differ_radar import build_radar, RadarResult
from envdiff.radar_formatter import format_radar_rich, format_radar_summary


def _write(tmp_path: Path, name: str, content: str) -> Path:
    p = tmp_path / name
    p.write_text(content)
    return p


def _result(tmp_path: Path, check_values: bool = False) -> RadarResult:
    base = _write(tmp_path, "base.env", "KEY=val\nOTHER=x\n")
    target = _write(tmp_path, "target.env", "KEY=val\n")
    diff = diff_pair(base, target, check_values=check_values)
    return build_radar([diff])


def test_empty_result_shows_no_data_message():
    out = format_radar_rich(RadarResult())
    assert "no radar data" in out.lower()


def test_rich_contains_header(tmp_path):
    out = format_radar_rich(_result(tmp_path))
    assert "Radar" in out


def test_rich_shows_coverage_axis(tmp_path):
    out = format_radar_rich(_result(tmp_path))
    assert "coverage" in out


def test_rich_shows_consistency_axis(tmp_path):
    out = format_radar_rich(_result(tmp_path))
    assert "consistency" in out


def test_rich_shows_overall(tmp_path):
    out = format_radar_rich(_result(tmp_path))
    assert "overall" in out


def test_rich_shows_target_path(tmp_path):
    out = format_radar_rich(_result(tmp_path))
    assert "target.env" in out


def test_summary_contains_overall_pct(tmp_path):
    out = format_radar_summary(_result(tmp_path))
    assert "overall=" in out
    assert "%" in out


def test_summary_empty_result():
    out = format_radar_summary(RadarResult())
    assert "no data" in out.lower()


def test_perfect_score_shows_100(tmp_path):
    base = _write(tmp_path, "base.env", "KEY=val\n")
    target = _write(tmp_path, "target.env", "KEY=val\n")
    diff = diff_pair(base, target, check_values=True)
    result = build_radar([diff])
    out = format_radar_summary(result)
    assert "100.0%" in out
