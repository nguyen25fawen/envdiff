"""Tests for envdiff.differ."""
from __future__ import annotations

from pathlib import Path

import pytest

from envdiff.differ import diff_pair, diff_many, EnvDiff, MultiDiff


def _write(tmp_path: Path, name: str, content: str) -> Path:
    p = tmp_path / name
    p.write_text(content, encoding="utf-8")
    return p


def test_diff_pair_no_differences(tmp_path):
    base = _write(tmp_path, "base.env", "FOO=bar\n")
    target = _write(tmp_path, "target.env", "FOO=bar\n")
    env_diff = diff_pair(base, target)
    assert isinstance(env_diff, EnvDiff)
    assert not env_diff.result.missing_in_second
    assert not env_diff.result.missing_in_first


def test_diff_pair_missing_in_target(tmp_path):
    base = _write(tmp_path, "base.env", "FOO=bar\nBAZ=1\n")
    target = _write(tmp_path, "target.env", "FOO=bar\n")
    env_diff = diff_pair(base, target)
    assert "BAZ" in env_diff.result.missing_in_second


def test_diff_pair_value_mismatch_detected(tmp_path):
    base = _write(tmp_path, "base.env", "FOO=bar\n")
    target = _write(tmp_path, "target.env", "FOO=baz\n")
    env_diff = diff_pair(base, target, check_values=True)
    assert "FOO" in env_diff.result.mismatched


def test_diff_pair_value_mismatch_skipped_by_default(tmp_path):
    base = _write(tmp_path, "base.env", "FOO=bar\n")
    target = _write(tmp_path, "target.env", "FOO=baz\n")
    env_diff = diff_pair(base, target)
    assert "FOO" not in env_diff.result.mismatched


def test_diff_many_returns_multi_diff(tmp_path):
    base = _write(tmp_path, "base.env", "FOO=1\n")
    t1 = _write(tmp_path, "t1.env", "FOO=1\n")
    t2 = _write(tmp_path, "t2.env", "FOO=1\nBAR=2\n")
    multi = diff_many(base, [t1, t2])
    assert isinstance(multi, MultiDiff)
    assert len(multi.diffs) == 2


def test_diff_many_any_differences_false(tmp_path):
    base = _write(tmp_path, "base.env", "FOO=1\n")
    t1 = _write(tmp_path, "t1.env", "FOO=1\n")
    multi = diff_many(base, [t1])
    assert not multi.any_differences()


def test_diff_many_any_differences_true(tmp_path):
    base = _write(tmp_path, "base.env", "FOO=1\nBAR=2\n")
    t1 = _write(tmp_path, "t1.env", "FOO=1\n")
    multi = diff_many(base, [t1])
    assert multi.any_differences()


def test_diff_pair_stores_paths(tmp_path):
    base = _write(tmp_path, "base.env", "K=v\n")
    target = _write(tmp_path, "tgt.env", "K=v\n")
    env_diff = diff_pair(base, target)
    assert env_diff.base_path == base
    assert env_diff.target_path == target
