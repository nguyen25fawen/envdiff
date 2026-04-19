"""Tests for envdiff.ignorer."""

from pathlib import Path

import pytest

from envdiff.ignorer import apply_ignore, filter_keys, is_ignored, load_ignore_patterns


def _write(tmp_path: Path, content: str) -> Path:
    p = tmp_path / ".envignore"
    p.write_text(content)
    return p


def test_load_ignores_comments(tmp_path):
    p = _write(tmp_path, "# this is a comment\nDEBUG\nSECRET_KEY\n")
    patterns = load_ignore_patterns(p)
    assert patterns == ["DEBUG", "SECRET_KEY"]


def test_load_ignores_blank_lines(tmp_path):
    p = _write(tmp_path, "\nFOO\n\nBAR\n")
    assert load_ignore_patterns(p) == ["FOO", "BAR"]


def test_is_ignored_exact_match():
    assert is_ignored("DEBUG", ["DEBUG"]) is True


def test_is_ignored_glob_wildcard():
    assert is_ignored("AWS_SECRET_KEY", ["AWS_*"]) is True


def test_is_ignored_glob_no_match():
    assert is_ignored("DATABASE_URL", ["AWS_*"]) is False


def test_is_ignored_regex_pattern():
    assert is_ignored("MY_TOKEN_123", ["re:TOKEN"]) is True


def test_is_ignored_regex_no_match():
    assert is_ignored("DATABASE_URL", ["re:^SECRET"]) is False


def test_is_ignored_no_patterns():
    assert is_ignored("ANY_KEY", []) is False


def test_filter_keys_removes_ignored():
    keys = ["DEBUG", "DATABASE_URL", "AWS_KEY"]
    result = filter_keys(keys, ["DEBUG", "AWS_*"])
    assert result == ["DATABASE_URL"]


def test_filter_keys_empty_patterns():
    keys = ["A", "B", "C"]
    assert filter_keys(keys, []) == keys


def test_apply_ignore_removes_keys():
    env = {"DEBUG": "true", "DATABASE_URL": "postgres://", "SECRET": "x"}
    result = apply_ignore(env, ["DEBUG", "SECRET"])
    assert result == {"DATABASE_URL": "postgres://"}


def test_apply_ignore_does_not_mutate_original():
    env = {"FOO": "1", "BAR": "2"}
    apply_ignore(env, ["FOO"])
    assert "FOO" in env


def test_apply_ignore_glob(tmp_path):
    env = {"AWS_ACCESS_KEY": "a", "AWS_SECRET": "b", "PORT": "8080"}
    result = apply_ignore(env, ["AWS_*"])
    assert result == {"PORT": "8080"}
