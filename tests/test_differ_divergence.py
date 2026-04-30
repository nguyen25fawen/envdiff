"""Tests for envdiff.differ_divergence."""
from __future__ import annotations

import pathlib

import pytest

from envdiff.differ_divergence import build_divergence


def _write(tmp_path: pathlib.Path, name: str, content: str) -> str:
    p = tmp_path / name
    p.write_text(content)
    return str(p)


def test_all_keys_present_in_result(tmp_path):
    a = _write(tmp_path, "a.env", "FOO=1\nBAR=2\n")
    b = _write(tmp_path, "b.env", "FOO=1\nBAZ=3\n")
    result = build_divergence([a, b])
    keys = [e.key for e in result.entries]
    assert "FOO" in keys
    assert "BAR" in keys
    assert "BAZ" in keys


def test_keys_sorted_alphabetically(tmp_path):
    a = _write(tmp_path, "a.env", "ZEBRA=1\nAPPLE=2\n")
    b = _write(tmp_path, "b.env", "MANGO=3\n")
    result = build_divergence([a, b])
    keys = [e.key for e in result.entries]
    assert keys == sorted(keys)


def test_uniform_key_when_values_equal(tmp_path):
    a = _write(tmp_path, "a.env", "FOO=same\n")
    b = _write(tmp_path, "b.env", "FOO=same\n")
    result = build_divergence([a, b])
    entry = next(e for e in result.entries if e.key == "FOO")
    assert entry.is_uniform is True
    assert entry.unique_values == 1


def test_diverged_key_when_values_differ(tmp_path):
    a = _write(tmp_path, "a.env", "FOO=one\n")
    b = _write(tmp_path, "b.env", "FOO=two\n")
    result = build_divergence([a, b])
    entry = next(e for e in result.entries if e.key == "FOO")
    assert entry.is_uniform is False
    assert entry.unique_values == 2


def test_absent_in_some_when_key_missing_from_file(tmp_path):
    a = _write(tmp_path, "a.env", "FOO=1\n")
    b = _write(tmp_path, "b.env", "BAR=2\n")
    result = build_divergence([a, b])
    foo = next(e for e in result.entries if e.key == "FOO")
    assert foo.is_absent_in_some is True


def test_uniform_keys_list(tmp_path):
    a = _write(tmp_path, "a.env", "FOO=x\nBAR=y\n")
    b = _write(tmp_path, "b.env", "FOO=x\nBAR=z\n")
    result = build_divergence([a, b])
    assert "FOO" in result.uniform_keys()
    assert "BAR" not in result.uniform_keys()


def test_diverged_keys_list(tmp_path):
    a = _write(tmp_path, "a.env", "FOO=x\nBAR=y\n")
    b = _write(tmp_path, "b.env", "FOO=x\nBAR=z\n")
    result = build_divergence([a, b])
    assert "BAR" in result.diverged_keys()
    assert "FOO" not in result.diverged_keys()


def test_files_recorded_in_result(tmp_path):
    a = _write(tmp_path, "a.env", "FOO=1\n")
    b = _write(tmp_path, "b.env", "FOO=1\n")
    result = build_divergence([a, b])
    assert a in result.files
    assert b in result.files


def test_single_file_all_uniform(tmp_path):
    a = _write(tmp_path, "a.env", "FOO=1\nBAR=2\n")
    result = build_divergence([a])
    assert all(e.is_uniform for e in result.entries)


def test_is_empty_when_no_keys(tmp_path):
    a = _write(tmp_path, "a.env", "")
    b = _write(tmp_path, "b.env", "")
    result = build_divergence([a, b])
    assert result.is_empty()
