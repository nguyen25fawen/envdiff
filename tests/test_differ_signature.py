"""Tests for envdiff.differ_signature and envdiff.signature_formatter."""
from __future__ import annotations

import pytest
from pathlib import Path

from envdiff.differ_signature import (
    build_signature,
    compare_signatures,
    unique_structures,
    structurally_equivalent,
    differing_keys,
)
from envdiff.signature_formatter import format_signature_rich, format_signature_summary


def _write(tmp_path: Path, name: str, content: str) -> Path:
    p = tmp_path / name
    p.write_text(content)
    return p


def test_build_signature_keys_sorted(tmp_path):
    f = _write(tmp_path, "a.env", "B=1\nA=2\nC=3\n")
    entry = build_signature(f)
    assert entry.keys == ["A", "B", "C"]


def test_build_signature_hex_length(tmp_path):
    f = _write(tmp_path, "a.env", "KEY=val\n")
    entry = build_signature(f)
    assert len(entry.signature) == 12
    assert all(c in "0123456789abcdef" for c in entry.signature)


def test_same_keys_same_signature(tmp_path):
    f1 = _write(tmp_path, "a.env", "A=1\nB=2\n")
    f2 = _write(tmp_path, "b.env", "A=99\nB=00\n")
    e1 = build_signature(f1)
    e2 = build_signature(f2)
    assert e1.signature == e2.signature


def test_different_keys_different_signature(tmp_path):
    f1 = _write(tmp_path, "a.env", "A=1\n")
    f2 = _write(tmp_path, "b.env", "B=1\n")
    e1 = build_signature(f1)
    e2 = build_signature(f2)
    assert e1.signature != e2.signature


def test_compare_signatures_groups_equivalent(tmp_path):
    f1 = _write(tmp_path, "a.env", "A=1\nB=2\n")
    f2 = _write(tmp_path, "b.env", "A=x\nB=y\n")
    result = compare_signatures([f1, f2])
    assert unique_structures(result) == 1
    assert structurally_equivalent(result)


def test_compare_signatures_detects_divergence(tmp_path):
    f1 = _write(tmp_path, "a.env", "A=1\n")
    f2 = _write(tmp_path, "b.env", "B=1\n")
    result = compare_signatures([f1, f2])
    assert unique_structures(result) == 2
    assert not structurally_equivalent(result)


def test_groups_contain_paths(tmp_path):
    f1 = _write(tmp_path, "a.env", "A=1\n")
    f2 = _write(tmp_path, "b.env", "A=2\n")
    f3 = _write(tmp_path, "c.env", "B=3\n")
    result = compare_signatures([f1, f2, f3])
    group_sizes = sorted(len(v) for v in result.groups.values())
    assert group_sizes == [1, 2]


def test_differing_keys_only_in_a(tmp_path):
    f1 = _write(tmp_path, "a.env", "A=1\nB=2\n")
    f2 = _write(tmp_path, "b.env", "A=1\n")
    e1 = build_signature(f1)
    e2 = build_signature(f2)
    diff = differing_keys(e1, e2)
    assert diff["only_in_a"] == {"B"}
    assert diff["only_in_b"] == set()


def test_format_signature_rich_contains_header(tmp_path):
    f = _write(tmp_path, "a.env", "A=1\n")
    result = compare_signatures([f])
    out = format_signature_rich(result)
    assert "Structural Signatures" in out


def test_format_signature_rich_shows_path(tmp_path):
    f = _write(tmp_path, "myfile.env", "X=1\n")
    result = compare_signatures([f])
    out = format_signature_rich(result)
    assert "myfile.env" in out


def test_format_signature_rich_show_keys(tmp_path):
    f = _write(tmp_path, "a.env", "FOO=1\nBAR=2\n")
    result = compare_signatures([f])
    out = format_signature_rich(result, show_keys=True)
    assert "FOO" in out
    assert "BAR" in out


def test_format_signature_summary_equivalent(tmp_path):
    f1 = _write(tmp_path, "a.env", "A=1\n")
    f2 = _write(tmp_path, "b.env", "A=2\n")
    result = compare_signatures([f1, f2])
    summary = format_signature_summary(result)
    assert "equivalent" in summary
    assert "2" in summary


def test_format_signature_summary_divergent(tmp_path):
    f1 = _write(tmp_path, "a.env", "A=1\n")
    f2 = _write(tmp_path, "b.env", "B=2\n")
    result = compare_signatures([f1, f2])
    summary = format_signature_summary(result)
    assert "divergent" in summary
