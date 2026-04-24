"""Tests for envdiff.differ_radar."""
from __future__ import annotations

import pytest
from pathlib import Path

from envdiff.differ import diff_pair
from envdiff.differ_radar import build_radar, RadarAxis, RadarEntry, RadarResult


def _write(tmp_path: Path, name: str, content: str) -> Path:
    p = tmp_path / name
    p.write_text(content)
    return p


def test_empty_diffs_returns_empty_result():
    result = build_radar([])
    assert result.is_empty()


def test_identical_files_full_score(tmp_path):
    base = _write(tmp_path, "base.env", "KEY=val\nOTHER=x\n")
    target = _write(tmp_path, "target.env", "KEY=val\nOTHER=x\n")
    diff = diff_pair(base, target, check_values=True)
    result = build_radar([diff])
    assert len(result.entries) == 1
    entry = result.entries[0]
    assert entry.overall == pytest.approx(1.0)


def test_missing_key_reduces_coverage(tmp_path):
    base = _write(tmp_path, "base.env", "KEY=val\nMISSING=x\n")
    target = _write(tmp_path, "target.env", "KEY=val\n")
    diff = diff_pair(base, target)
    result = build_radar([diff])
    entry = result.entries[0]
    cov_axis = next(a for a in entry.axes if a.name == "coverage")
    assert cov_axis.score < 1.0


def test_value_mismatch_reduces_consistency(tmp_path):
    base = _write(tmp_path, "base.env", "KEY=val1\n")
    target = _write(tmp_path, "target.env", "KEY=val2\n")
    diff = diff_pair(base, target, check_values=True)
    result = build_radar([diff])
    entry = result.entries[0]
    con_axis = next(a for a in entry.axes if a.name == "consistency")
    assert con_axis.score < 1.0


def test_multiple_targets_produce_multiple_entries(tmp_path):
    base = _write(tmp_path, "base.env", "KEY=val\n")
    t1 = _write(tmp_path, "t1.env", "KEY=val\n")
    t2 = _write(tmp_path, "t2.env", "KEY=other\n")
    diffs = [
        diff_pair(base, t1, check_values=True),
        diff_pair(base, t2, check_values=True),
    ]
    result = build_radar(diffs)
    assert len(result.entries) == 2


def test_overall_is_mean_of_axes(tmp_path):
    base = _write(tmp_path, "base.env", "A=1\nB=2\n")
    target = _write(tmp_path, "target.env", "A=1\n")
    diff = diff_pair(base, target)
    result = build_radar([diff])
    entry = result.entries[0]
    expected = sum(a.score for a in entry.axes) / len(entry.axes)
    assert entry.overall == pytest.approx(expected)


def test_radar_entry_path_matches_target(tmp_path):
    base = _write(tmp_path, "base.env", "KEY=val\n")
    target = _write(tmp_path, "target.env", "KEY=val\n")
    diff = diff_pair(base, target)
    result = build_radar([diff])
    assert str(target) in result.entries[0].path


def test_axes_have_names_coverage_and_consistency(tmp_path):
    base = _write(tmp_path, "base.env", "KEY=val\n")
    target = _write(tmp_path, "target.env", "KEY=val\n")
    diff = diff_pair(base, target)
    result = build_radar([diff])
    names = {a.name for a in result.entries[0].axes}
    assert "coverage" in names
    assert "consistency" in names
