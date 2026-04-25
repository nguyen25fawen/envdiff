"""Tests for envdiff.topology_formatter."""
from __future__ import annotations

import pathlib

from envdiff.differ_topology import build_topology, TopologyResult
from envdiff.topology_formatter import format_topology_rich, format_topology_summary


def _write(tmp_path: pathlib.Path, name: str, content: str) -> str:
    p = tmp_path / name
    p.write_text(content)
    return str(p)


def _result(tmp_path: pathlib.Path):
    a = _write(tmp_path, "a.env", "X=1\nY=2\n")
    b = _write(tmp_path, "b.env", "Y=2\nZ=3\n")
    return build_topology([a, b])


def test_empty_result_shows_message():
    out = format_topology_rich(TopologyResult())
    assert "No files" in out


def test_rich_contains_header(tmp_path):
    out = format_topology_rich(_result(tmp_path))
    assert "Topology" in out


def test_rich_shows_node_path(tmp_path):
    a = _write(tmp_path, "a.env", "X=1\n")
    b = _write(tmp_path, "b.env", "Y=2\n")
    result = build_topology([a, b])
    out = format_topology_rich(result)
    assert "a.env" in out
    assert "b.env" in out


def test_rich_shows_overlap_pct(tmp_path):
    a = _write(tmp_path, "a.env", "X=1\nY=2\n")
    b = _write(tmp_path, "b.env", "X=1\nY=2\n")
    result = build_topology([a, b])
    out = format_topology_rich(result)
    assert "100.0%" in out


def test_show_shared_lists_keys(tmp_path):
    a = _write(tmp_path, "a.env", "SHARED=1\nONLY_A=2\n")
    b = _write(tmp_path, "b.env", "SHARED=1\nONLY_B=3\n")
    result = build_topology([a, b])
    out = format_topology_rich(result, show_shared=True)
    assert "SHARED" in out


def test_summary_contains_file_count(tmp_path):
    out = format_topology_summary(_result(tmp_path))
    assert "2 files" in out


def test_summary_contains_pair_count(tmp_path):
    out = format_topology_summary(_result(tmp_path))
    assert "1 pairs" in out


def test_summary_empty_result():
    out = format_topology_summary(TopologyResult())
    assert "no files" in out


def test_summary_avg_overlap(tmp_path):
    a = _write(tmp_path, "a.env", "X=1\nY=2\n")
    b = _write(tmp_path, "b.env", "X=1\nY=2\n")
    result = build_topology([a, b])
    out = format_topology_summary(result)
    assert "100.0%" in out
