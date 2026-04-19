"""Tests for envdiff.pinner."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from envdiff.pinner import (
    diff_pin,
    format_pin_diff,
    load_pin,
    pin_env,
    save_pin,
)


def _write(tmp_path: Path, name: str, content: str) -> Path:
    p = tmp_path / name
    p.write_text(content, encoding="utf-8")
    return p


def test_pin_env_basic(tmp_path: Path) -> None:
    f = _write(tmp_path, ".env", "FOO=bar\nBAZ=qux\n")
    result = pin_env(f)
    assert result == {"FOO": "bar", "BAZ": "qux"}


def test_pin_env_empty(tmp_path: Path) -> None:
    f = _write(tmp_path, ".env", "")
    assert pin_env(f) == {}


def test_save_and_load_pin(tmp_path: Path) -> None:
    data = {"KEY": "value", "OTHER": "123"}
    out = tmp_path / "pins" / "lock.json"
    save_pin(data, out)
    assert out.exists()
    loaded = load_pin(out)
    assert loaded == data


def test_save_pin_creates_parents(tmp_path: Path) -> None:
    out = tmp_path / "a" / "b" / "c.json"
    save_pin({"X": "1"}, out)
    assert out.exists()


def test_save_pin_is_sorted_json(tmp_path: Path) -> None:
    out = tmp_path / "lock.json"
    save_pin({"Z": "1", "A": "2"}, out)
    raw = json.loads(out.read_text())
    assert list(raw.keys()) == ["A", "Z"]


def test_diff_pin_no_drift() -> None:
    pinned = {"A": "1", "B": "2"}
    current = {"A": "1", "B": "2"}
    result = diff_pin(pinned, current)
    assert result == {"added": [], "removed": [], "changed": []}


def test_diff__key() -> None:
    result = diff_pin({"A": "1"}, {"A": "1", "B": "2"})
    assert result["added"] == ["B"]
    assert result["removed"] == []
    assert result["changed"] == []


def test_diff_pin_removed_key() -> None:
    result = diff_pin({"A": "1", "B": "2"}, {"A": "1"})
    assert result["removed"] == ["B"]


def test_diff_pin_changed_value() -> None:
    result = diff_pin({"A": "old"}, {"A": "new"})
    assert result["changed"] == ["A"]


def test_format_pin_diff_no_drift() -> None:
    msg = format_pin_diff({"added": [], "removed": [], "changed": []})
    assert "No drift" in msg


def test_format_pin_diff_shows_changes() -> None:
    result = {"added": ["NEW"], "removed": ["OLD"], "changed": ["MOD"]}
    msg = format_pin_diff(result)
    assert "NEW" in msg
    assert "OLD" in msg
    assert "MOD" in msg
    assert "3 change" in msg
