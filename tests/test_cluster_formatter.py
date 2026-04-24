"""Tests for envdiff.cluster_formatter."""
from __future__ import annotations

import pathlib

import pytest

from envdiff.differ_cluster import ClusterEntry, ClusterResult, cluster_files
from envdiff.cluster_formatter import format_cluster_rich, format_cluster_summary


def _write(tmp_path: pathlib.Path, name: str, content: str) -> str:
    p = tmp_path / name
    p.write_text(content)
    return str(p)


def _result(tmp_path, threshold=0.5):
    f1 = _write(tmp_path, ".env.a", "A=1\nB=2\n")
    f2 = _write(tmp_path, ".env.b", "A=1\nB=2\n")
    f3 = _write(tmp_path, ".env.c", "X=9\n")
    return cluster_files([f1, f2, f3], threshold=threshold)


def test_empty_result_message():
    result = ClusterResult(entries=[], groups=[])
    out = format_cluster_rich(result)
    assert "No files" in out


def test_rich_contains_header(tmp_path):
    result = _result(tmp_path)
    out = format_cluster_rich(result)
    assert "Cluster Report" in out


def test_rich_shows_group_label(tmp_path):
    result = _result(tmp_path)
    out = format_cluster_rich(result)
    assert "Group 1" in out


def test_rich_shows_file_path(tmp_path):
    f1 = _write(tmp_path, ".env.x", "A=1\n")
    result = cluster_files([f1])
    out = format_cluster_rich(result)
    assert ".env.x" in out


def test_similarity_hidden_by_default(tmp_path):
    result = _result(tmp_path)
    out = format_cluster_rich(result, show_similarity=False)
    assert "shared" not in out


def test_similarity_shown_when_flag_set(tmp_path):
    f1 = _write(tmp_path, ".env.a", "A=1\nB=2\n")
    f2 = _write(tmp_path, ".env.b", "A=1\nB=2\n")
    result = cluster_files([f1, f2], threshold=0.5)
    out = format_cluster_rich(result, show_similarity=True)
    assert "shared" in out


def test_summary_contains_file_count(tmp_path):
    result = _result(tmp_path)
    summary = format_cluster_summary(result)
    assert "3 file" in summary


def test_summary_contains_group_count(tmp_path):
    result = _result(tmp_path)
    summary = format_cluster_summary(result)
    assert "cluster" in summary


def test_summary_empty():
    result = ClusterResult(entries=[], groups=[])
    summary = format_cluster_summary(result)
    assert "No files" in summary
