"""Tests for envdiff.differ_sketch and envdiff.sketch_formatter."""
from __future__ import annotations

import pytest

from envdiff.differ_sketch import _minhash, _jaccard_from_minhash, build_sketch
from envdiff.sketch_formatter import format_sketch_rich, format_sketch_summary


# ---------------------------------------------------------------------------
# _minhash
# ---------------------------------------------------------------------------

def test_minhash_empty_returns_zeros():
    result = _minhash([], num_hashes=8)
    assert result == [0] * 8


def test_minhash_length_matches_num_hashes():
    result = _minhash(["A", "B", "C"], num_hashes=16)
    assert len(result) == 16


def test_minhash_deterministic():
    keys = ["FOO", "BAR", "BAZ"]
    assert _minhash(keys, 32) == _minhash(keys, 32)


def test_minhash_different_keys_likely_different():
    a = _minhash(["X", "Y"], 64)
    b = _minhash(["P", "Q"], 64)
    assert a != b


# ---------------------------------------------------------------------------
# _jaccard_from_minhash
# ---------------------------------------------------------------------------

def test_jaccard_identical_signatures():
    sig = [1, 2, 3, 4]
    assert _jaccard_from_minhash(sig, sig) == 1.0


def test_jaccard_empty_signatures():
    assert _jaccard_from_minhash([], []) == 0.0


def test_jaccard_partial_overlap():
    a = [1, 2, 3, 4]
    b = [1, 2, 9, 9]
    assert _jaccard_from_minhash(a, b) == pytest.approx(0.5)


# ---------------------------------------------------------------------------
# build_sketch
# ---------------------------------------------------------------------------

def test_build_sketch_empty():
    result = build_sketch({})
    assert result.is_empty()


def test_build_sketch_single_file():
    result = build_sketch({"a.env": {"FOO": "1", "BAR": "2"}}, num_hashes=16)
    assert len(result.entries) == 1
    assert result.entries[0].path == "a.env"
    assert result.similarity_matrix["a.env"]["a.env"] == 1.0


def test_build_sketch_identical_files_high_similarity():
    env = {"A": "1", "B": "2", "C": "3"}
    result = build_sketch({"x.env": env, "y.env": env}, num_hashes=64)
    sim = result.similarity_matrix["x.env"]["y.env"]
    assert sim > 0.9


def test_build_sketch_disjoint_files_low_similarity():
    result = build_sketch(
        {"a.env": {f"K{i}": str(i) for i in range(20)},
         "b.env": {f"Z{i}": str(i) for i in range(20)}},
        num_hashes=64,
    )
    sim = result.similarity_matrix["a.env"]["b.env"]
    assert sim < 0.3


def test_build_sketch_keys_recorded():
    result = build_sketch({"e.env": {"FOO": "bar", "BAZ": "qux"}}, num_hashes=8)
    assert set(result.entries[0].keys) == {"FOO", "BAZ"}


# ---------------------------------------------------------------------------
# formatter
# ---------------------------------------------------------------------------

def test_format_sketch_rich_empty():
    from envdiff.differ_sketch import SketchResult
    out = format_sketch_rich(SketchResult())
    assert "No env files" in out


def test_format_sketch_rich_contains_header():
    result = build_sketch({"a.env": {"A": "1"}, "b.env": {"A": "1"}}, num_hashes=16)
    out = format_sketch_rich(result)
    assert "Sketch" in out or "sketch" in out.lower() or "Similarity" in out


def test_format_sketch_summary_single_file():
    result = build_sketch({"only.env": {"X": "1"}}, num_hashes=8)
    summary = format_sketch_summary(result)
    assert "1 file" in summary
    assert "only.env" in summary


def test_format_sketch_summary_two_files():
    result = build_sketch({"a.env": {"A": "1"}, "b.env": {"A": "1"}}, num_hashes=32)
    summary = format_sketch_summary(result)
    assert "a.env" in summary
    assert "b.env" in summary
