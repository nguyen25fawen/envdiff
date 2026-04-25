"""Tests for envdiff.differ_topology."""
from __future__ import annotations

import pathlib

import pytest

from envdiff.differ_topology import (
    TopologyNode,
    TopologyEdge,
    TopologyResult,
    _jaccard,
    build_topology,
)


def _write(tmp_path: pathlib.Path, name: str, content: str) -> str:
    p = tmp_path / name
    p.write_text(content)
    return str(p)


def test_jaccard_identical():
    s = frozenset({"A", "B", "C"})
    assert _jaccard(s, s) == 1.0


def test_jaccard_disjoint():
    assert _jaccard(frozenset({"A"}), frozenset({"B"})) == 0.0


def test_jaccard_partial():
    a = frozenset({"A", "B"})
    b = frozenset({"B", "C"})
    assert _jaccard(a, b) == pytest.approx(1 / 3)


def test_jaccard_both_empty():
    assert _jaccard(frozenset(), frozenset()) == 1.0


def test_build_topology_nodes(tmp_path):
    a = _write(tmp_path, "a.env", "X=1\nY=2\n")
    b = _write(tmp_path, "b.env", "Y=2\nZ=3\n")
    result = build_topology([a, b])
    assert len(result.nodes) == 2
    paths = {n.path for n in result.nodes}
    assert a in paths and b in paths


def test_build_topology_key_count(tmp_path):
    a = _write(tmp_path, "a.env", "X=1\nY=2\n")
    b = _write(tmp_path, "b.env", "Y=2\n")
    result = build_topology([a, b])
    node_a = result.node_for(a)
    assert node_a is not None
    assert node_a.key_count == 2


def test_build_topology_single_edge(tmp_path):
    a = _write(tmp_path, "a.env", "X=1\nY=2\n")
    b = _write(tmp_path, "b.env", "Y=2\nZ=3\n")
    result = build_topology([a, b])
    assert len(result.edges) == 1


def test_build_topology_shared_keys(tmp_path):
    a = _write(tmp_path, "a.env", "X=1\nY=2\n")
    b = _write(tmp_path, "b.env", "Y=2\nZ=3\n")
    result = build_topology([a, b])
    edge = result.edges[0]
    assert "Y" in edge.shared_keys
    assert "X" not in edge.shared_keys


def test_build_topology_overlap_pct(tmp_path):
    a = _write(tmp_path, "a.env", "A=1\nB=2\nC=3\n")
    b = _write(tmp_path, "b.env", "A=1\nB=2\nC=3\n")
    result = build_topology([a, b])
    assert result.edges[0].overlap_pct == 100.0


def test_build_topology_three_files_edge_count(tmp_path):
    a = _write(tmp_path, "a.env", "A=1\n")
    b = _write(tmp_path, "b.env", "B=2\n")
    c = _write(tmp_path, "c.env", "C=3\n")
    result = build_topology([a, b, c])
    assert len(result.edges) == 3


def test_is_empty_with_no_nodes():
    assert TopologyResult().is_empty()


def test_edges_for_path(tmp_path):
    a = _write(tmp_path, "a.env", "X=1\n")
    b = _write(tmp_path, "b.env", "X=1\n")
    c = _write(tmp_path, "c.env", "X=1\n")
    result = build_topology([a, b, c])
    edges_a = result.edges_for(a)
    assert len(edges_a) == 2
