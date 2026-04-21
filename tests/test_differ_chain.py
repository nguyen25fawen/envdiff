"""Tests for envdiff.differ_chain."""
from __future__ import annotations

import pathlib

import pytest

from envdiff.differ_chain import build_chain


def _write(tmp_path: pathlib.Path, name: str, content: str) -> str:
    p = tmp_path / name
    p.write_text(content)
    return str(p)


def test_single_file_all_keys_present(tmp_path):
    f = _write(tmp_path, "a.env", "FOO=bar\nBAZ=qux\n")
    result = build_chain([f])
    assert set(result.all_keys()) == {"FOO", "BAZ"}


def test_first_wins_by_default(tmp_path):
    f1 = _write(tmp_path, "first.env", "KEY=from_first\n")
    f2 = _write(tmp_path, "second.env", "KEY=from_second\n")
    result = build_chain([f1, f2])
    assert result.entries["KEY"].final_value == "from_first"
    assert result.entries["KEY"].origin == f1


def test_last_wins_flag(tmp_path):
    f1 = _write(tmp_path, "first.env", "KEY=from_first\n")
    f2 = _write(tmp_path, "second.env", "KEY=from_second\n")
    result = build_chain([f1, f2], last_wins=True)
    assert result.entries["KEY"].final_value == "from_second"
    assert result.entries["KEY"].origin == f2


def test_union_of_keys(tmp_path):
    f1 = _write(tmp_path, "a.env", "ALPHA=1\n")
    f2 = _write(tmp_path, "b.env", "BETA=2\n")
    result = build_chain([f1, f2])
    assert "ALPHA" in result.all_keys()
    assert "BETA" in result.all_keys()


def test_was_overridden_true(tmp_path):
    f1 = _write(tmp_path, "base.env", "X=1\n")
    f2 = _write(tmp_path, "override.env", "X=2\n")
    result = build_chain([f1, f2])
    # f1 wins; f2 is shadowed — overridden_by should contain f2
    assert result.was_overridden("X")
    assert f2 in result.entries["X"].overridden_by


def test_was_overridden_false_when_unique(tmp_path):
    f1 = _write(tmp_path, "only.env", "ONLY=yes\n")
    result = build_chain([f1])
    assert not result.was_overridden("ONLY")


def test_origin_of_returns_correct_path(tmp_path):
    f1 = _write(tmp_path, "a.env", "DB=postgres\n")
    f2 = _write(tmp_path, "b.env", "CACHE=redis\n")
    result = build_chain([f1, f2])
    assert result.origin_of("DB") == f1
    assert result.origin_of("CACHE") == f2


def test_origin_of_missing_key_returns_none(tmp_path):
    f = _write(tmp_path, "a.env", "FOO=bar\n")
    result = build_chain([f])
    assert result.origin_of("MISSING") is None


def test_introduced_at_tracks_first_file(tmp_path):
    f1 = _write(tmp_path, "base.env", "NEW_KEY=hello\n")
    f2 = _write(tmp_path, "extra.env", "NEW_KEY=world\n")
    result = build_chain([f1, f2])
    assert result.entries["NEW_KEY"].introduced_at == f1


def test_three_files_precedence(tmp_path):
    f1 = _write(tmp_path, "1.env", "V=first\n")
    f2 = _write(tmp_path, "2.env", "V=second\n")
    f3 = _write(tmp_path, "3.env", "V=third\n")
    result = build_chain([f1, f2, f3])
    assert result.entries["V"].final_value == "first"
    assert len(result.entries["V"].overridden_by) == 2


def test_links_count_matches_input(tmp_path):
    files = [
        _write(tmp_path, f"{i}.env", f"K{i}=v{i}\n") for i in range(4)
    ]
    result = build_chain(files)
    assert len(result.links) == 4
