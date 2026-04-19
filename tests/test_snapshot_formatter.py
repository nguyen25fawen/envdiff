"""Tests for envdiff.snapshot_formatter."""
import pytest

from envdiff.snapshot_formatter import format_drift, format_snapshot_summary


def _no_drift():
    return {
        "old_label": "v1",
        "new_label": "v2",
        "old_timestamp": "2024-01-01T00:00:00+00:00",
        "new_timestamp": "2024-06-01T00:00:00+00:00",
        "added": [],
        "removed": [],
        "changed": [],
        "drift_detected": False,
    }


def _with_drift(**kwargs):
    base = _no_drift()
    base["drift_detected"] = True
    base.update(kwargs)
    return base


def test_no_drift_message():
    out = format_drift(_no_drift())
    assert "No drift detected" in out


def test_added_key_shown():
    out = format_drift(_with_drift(added=["NEW_KEY"]))
    assert "NEW_KEY" in out
    assert "added" in out


def test_removed_key_shown():
    out = format_drift(_with_drift(removed=["OLD_KEY"]))
    assert "OLD_KEY" in out
    assert "removed" in out


def test_changed_key_shown():
    out = format_drift(_with_drift(changed=["MOD_KEY"]))
    assert "MOD_KEY" in out
    assert "changed" in out


def test_header_contains_labels():
    out = format_drift(_no_drift())
    assert "v1" in out
    assert "v2" in out


def test_format_snapshot_summary_fields():
    snap = {
        "label": "staging",
        "source": ".env.staging",
        "timestamp": "2024-01-01T00:00:00+00:00",
        "hash": "abc123",
        "keys": ["A", "B", "C"],
    }
    out = format_snapshot_summary(snap)
    assert "staging" in out
    assert "abc123" in out
    assert "3" in out
