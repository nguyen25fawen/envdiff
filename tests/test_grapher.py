"""Tests for envdiff.grapher."""
import pytest
from envdiff.grapher import build_graph, format_graph, GraphResult


def _env(**kwargs: str) -> dict:
    return dict(kwargs)


def test_no_references():
    result = build_graph(_env(FOO="bar", BAZ="qux"))
    assert set(result.roots) == {"FOO", "BAZ"}
    assert result.orphans == []
    assert result.cycles == []


def test_simple_dependency():
    result = build_graph(_env(A="hello", B="${A}_world"))
    assert "A" in result.edges["B"]
    assert "B" in result.roots or "A" in result.roots


def test_orphan_reference():
    result = build_graph(_env(A="${UNDEFINED}"))
    assert "UNDEFINED" in result.orphans


def test_multiple_orphans_sorted():
    result = build_graph(_env(A="${Z} and ${M}"))
    assert result.orphans == ["M", "Z"]


def test_cycle_detected():
    result = build_graph(_env(A="${B}", B="${A}"))
    assert len(result.cycles) >= 1


def test_no_cycle_for_chain():
    result = build_graph(_env(A="hello", B="${A}", C="${B}"))
    # no cycles in a straight chain
    assert result.cycles == []


def test_roots_have_no_deps():
    result = build_graph(_env(A="plain", B="${A}"))
    assert "A" in result.roots
    assert "B" not in result.roots


def test_dollar_plain_ref():
    result = build_graph(_env(HOST="localhost", URL="http://$HOST/path"))
    assert "HOST" in result.edges["URL"]


def test_format_graph_contains_key_info():
    result = build_graph(_env(A="${MISSING}"))
    text = format_graph(result)
    assert "MISSING" in text
    assert "Orphans" in text or "Undefined" in text


def test_format_graph_cycle_shown():
    result = build_graph(_env(A="${B}", B="${A}"))
    text = format_graph(result)
    assert "Cycle" in text or "->" in text


def test_empty_env():
    result = build_graph({})
    assert result.roots == []
    assert result.orphans == []
    assert result.cycles == []
