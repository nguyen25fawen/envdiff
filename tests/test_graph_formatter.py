"""Tests for envdiff.graph_formatter."""
from envdiff.grapher import build_graph, GraphResult
from envdiff.graph_formatter import format_graph_rich, format_graph_summary


def _result(**kwargs: str) -> GraphResult:
    return build_graph(dict(kwargs))


def test_rich_contains_header():
    r = _result(A="plain")
    out = format_graph_rich(r)
    assert "Dependency Graph" in out


def test_rich_shows_orphan():
    r = _result(A="${MISSING}")
    out = format_graph_rich(r)
    assert "MISSING" in out


def test_rich_shows_cycle():
    r = _result(A="${B}", B="${A}")
    out = format_graph_rich(r)
    assert "Cycle" in out or "->" in out


def test_rich_no_issues_no_orphan_section():
    r = _result(A="hello", B="world")
    out = format_graph_rich(r)
    assert "Undefined" not in out


def test_rich_show_all_includes_deps():
    r = _result(A="plain", B="${A}")
    out = format_graph_rich(r, show_all=True)
    assert "A" in out
    assert "B" in out


def test_summary_ok_status():
    r = _result(A="hello")
    s = format_graph_summary(r)
    assert "OK" in s


def test_summary_issues_status():
    r = _result(A="${UNDEFINED}")
    s = format_graph_summary(r)
    assert "ISSUES" in s


def test_summary_counts():
    r = _result(A="hello", B="${A}", C="${MISSING}")
    s = format_graph_summary(r)
    assert "3 keys" in s
    assert "1 orphans" in s
