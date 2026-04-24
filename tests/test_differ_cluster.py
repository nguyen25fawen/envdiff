"""Tests for envdiff.differ_cluster."""
from __future__ import annotations

import pathlib
import pytest

from envdiff.differ_cluster import (
    ClusterEntry,
    ClusterResult,
    _jaccard,
    cluster_files,
)


def _write(tmp_path: pathlib.Path, name: str, content: str) -> str:
    p = tmp_path / name
    p.write_text(content)
    return str(p)


def test_jaccard_identical():
    a = frozenset(["A", "B", "C"])
    assert _jaccard(a, a) == 1.0


def test_jaccard_disjoint():
    a = frozenset(["A"])
    b = frozenset(["B"])
    assert _jaccard(a, b) == 0.0


def test_jaccard_partial():
    a = frozenset(["A", "B"])
    b = frozenset(["B", "C"])
    # intersection=1, union=3
    assert abs(_jaccard(a, b) - 1 / 3) < 1e-9


def test_jaccard_empty_both():
    assert _jaccard(frozenset(), frozenset()) == 1.0


def test_cluster_empty_list():
    result = cluster_files([])
    assert result.is_empty()
    assert result.groups == []


def test_cluster_single_file(tmp_path):
    f = _write(tmp_path, ".env", "A=1\nB=2\n")
    result = cluster_files([f])
    assert len(result.groups) == 1
    assert result.groups[0] == [f]


def test_identical_files_clustered_together(tmp_path):
    f1 = _write(tmp_path, ".env.a", "A=1\nB=2\n")
    f2 = _write(tmp_path, ".env.b", "A=1\nB=2\n")
    result = cluster_files([f1, f2], threshold=0.5)
    assert any(f1 in g and f2 in g for g in result.groups)


def test_disjoint_files_in_separate_groups(tmp_path):
    f1 = _write(tmp_path, ".env.a", "A=1\n")
    f2 = _write(tmp_path, ".env.b", "Z=9\n")
    result = cluster_files([f1, f2], threshold=0.5)
    assert len(result.groups) == 2


def test_similarity_stored_in_entry(tmp_path):
    f1 = _write(tmp_path, ".env.a", "A=1\nB=2\n")
    f2 = _write(tmp_path, ".env.b", "A=1\nC=3\n")
    result = cluster_files([f1, f2])
    entry = next(e for e in result.entries if e.path == f1)
    assert f2 in entry.shared_with
    assert 0.0 < entry.shared_with[f2] <= 1.0


def test_three_files_two_clusters(tmp_path):
    f1 = _write(tmp_path, ".env.a", "A=1\nB=2\n")
    f2 = _write(tmp_path, ".env.b", "A=1\nB=2\n")
    f3 = _write(tmp_path, ".env.c", "X=9\nY=8\n")
    result = cluster_files([f1, f2, f3], threshold=0.5)
    assert len(result.groups) == 2


def test_high_threshold_splits_partial_overlap(tmp_path):
    f1 = _write(tmp_path, ".env.a", "A=1\nB=2\nC=3\nD=4\n")
    f2 = _write(tmp_path, ".env.b", "A=1\nX=9\nY=8\nZ=7\n")
    # jaccard = 1/7 ≈ 0.14, well below 0.9
    result = cluster_files([f1, f2], threshold=0.9)
    assert len(result.groups) == 2
