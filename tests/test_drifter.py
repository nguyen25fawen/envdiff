"""Tests for envdiff.drifter."""
import os
import pytest
from pathlib import Path

from envdiff.drifter import drift_pair, drift_many, DriftEntry


def _write(tmp_path: Path, name: str, content: str) -> str:
    p = tmp_path / name
    p.write_text(content)
    return str(p)


def test_no_drift_identical_files(tmp_path):
    base = _write(tmp_path, "base.env", "A=1\nB=2\n")
    target = _write(tmp_path, "target.env", "A=1\nB=2\n")
    report = drift_pair(base, target)
    assert not report.has_drift()


def test_removed_key_detected(tmp_path):
    base = _write(tmp_path, "base.env", "A=1\nB=2\n")
    target = _write(tmp_path, "target.env", "A=1\n")
    report = drift_pair(base, target)
    assert report.has_drift()
    removed = report.by_kind("removed")
    assert any(e.key == "B" for e in removed)


def test_added_key_detected(tmp_path):
    base = _write(tmp_path, "base.env", "A=1\n")
    target = _write(tmp_path, "target.env", "A=1\nC=3\n")
    report = drift_pair(base, target)
    added = report.by_kind("added")
    assert any(e.key == "C" for e in added)


def test_changed_value_detected(tmp_path):
    base = _write(tmp_path, "base.env", "A=hello\n")
    target = _write(tmp_path, "target.env", "A=world\n")
    report = drift_pair(base, target, check_values=True)
    changed = report.by_kind("changed")
    assert any(e.key == "A" for e in changed)


def test_changed_value_skipped_when_flag_off(tmp_path):
    base = _write(tmp_path, "base.env", "A=hello\n")
    target = _write(tmp_path, "target.env", "A=world\n")
    report = drift_pair(base, target, check_values=False)
    assert not report.has_drift()


def test_drift_many_returns_one_report_per_target(tmp_path):
    base = _write(tmp_path, "base.env", "A=1\n")
    t1 = _write(tmp_path, "t1.env", "A=1\n")
    t2 = _write(tmp_path, "t2.env", "B=2\n")
    reports = drift_many(base, [t1, t2])
    assert len(reports) == 2
    assert not reports[0].has_drift()
    assert reports[1].has_drift()


def test_entry_values_stored(tmp_path):
    base = _write(tmp_path, "base.env", "X=old\n")
    target = _write(tmp_path, "target.env", "X=new\n")
    report = drift_pair(base, target)
    entry = report.by_kind("changed")[0]
    assert entry.base_value == "old"
    assert entry.target_value == "new"
