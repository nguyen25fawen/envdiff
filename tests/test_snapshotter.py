"""Tests for envdiff.snapshotter."""
import json
from pathlib import Path

import pytest

from envdiff.snapshotter import (
    take_snapshot,
    save_snapshot,
    load_snapshot,
    diff_snapshots,
)


def _write(tmp_path: Path, name: str, content: str) -> Path:
    p = tmp_path / name
    p.write_text(content)
    return p


def test_take_snapshot_keys(tmp_path):
    f = _write(tmp_path, ".env", "FOO=bar\nBAZ=qux\n")
    snap = take_snapshot(f)
    assert "FOO" in snap["keys"]
    assert "BAZ" in snap["keys"]


def test_take_snapshot_has_hash(tmp_path):
    f = _write(tmp_path, ".env", "KEY=val\n")
    snap = take_snapshot(f)
    assert len(snap["hash"]) == 16


def test_take_snapshot_label_default(tmp_path):
    f = _write(tmp_path, "prod.env", "X=1\n")
    snap = take_snapshot(f)
    assert snap["label"] == "prod.env"


def test_take_snapshot_custom_label(tmp_path):
    f = _write(tmp_path, ".env", "X=1\n")
    snap = take_snapshot(f, label="production")
    assert snap["label"] == "production"


def test_save_and_load_roundtrip(tmp_path):
    f = _write(tmp_path, ".env", "A=1\nB=2\n")
    snap = take_snapshot(f)
    out = tmp_path / "snapshots" / "snap.json"
    save_snapshot(snap, out)
    loaded = load_snapshot(out)
    assert loaded["hash"] == snap["hash"]
    assert loaded["entries"] == snap["entries"]


def test_diff_no_drift():
    base = {"label": "a", "timestamp": "t1", "entries": {"K": "v"}}
    new = {"label": "b", "timestamp": "t2", "entries": {"K": "v"}}
    report = diff_snapshots(base, new)
    assert not report["drift_detected"]
    assert report["added"] == []
    assert report["removed"] == []
    assert report["changed"] == []


def test_diff_detects_added():
    old = {"entries": {"A": "1"}}
    new = {"entries": {"A": "1", "B": "2"}}
    report = diff_snapshots(old, new)
    assert "B" in report["added"]
    assert report["drift_detected"]


def test_diff_detects_removed():
    old = {"entries": {"A": "1", "B": "2"}}
    new = {"entries": {"A": "1"}}
    report = diff_snapshots(old, new)
    assert "B" in report["removed"]


def test_diff_detects_changed():
    old = {"entries": {"A": "old"}}
    new = {"entries": {"A": "new"}}
    report = diff_snapshots(old, new)
    assert "A" in report["changed"]
