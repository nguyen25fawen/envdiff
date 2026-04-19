"""Tests for envdiff.tagger."""
from pathlib import Path

import pytest

from envdiff.tagger import TagResult, load_tag_rules, tag_keys, tag_env


def _write(tmp_path: Path, content: str) -> Path:
    p = tmp_path / "tags.conf"
    p.write_text(content)
    return p


def test_load_tag_rules_basic(tmp_path):
    p = _write(tmp_path, "database: DB_*, POSTGRES_*\nsecrets: *SECRET*, *PASSWORD*\n")
    rules = load_tag_rules(p)
    assert "database" in rules
    assert "DB_*" in rules["database"]
    assert "POSTGRES_*" in rules["database"]
    assert "secrets" in rules


def test_load_tag_rules_ignores_comments(tmp_path):
    p = _write(tmp_path, "# this is a comment\ndatabase: DB_*\n")
    rules = load_tag_rules(p)
    assert list(rules.keys()) == ["database"]


def test_load_tag_rules_ignores_blank_lines(tmp_path):
    p = _write(tmp_path, "\ndatabase: DB_*\n\n")
    rules = load_tag_rules(p)
    assert "database" in rules


def test_load_tag_rules_no_colon_skipped(tmp_path):
    p = _write(tmp_path, "invalid line\ndatabase: DB_*\n")
    rules = load_tag_rules(p)
    assert list(rules.keys()) == ["database"]


def test_tag_keys_exact_glob(tmp_path):
    rules = {"database": ["DB_*"]}
    result = tag_keys(["DB_HOST", "DB_PORT", "APP_NAME"], rules)
    assert "DB_HOST" in result.tags
    assert "DB_PORT" in result.tags
    assert "APP_NAME" not in result.tags


def test_tag_keys_multiple_tags(tmp_path):
    rules = {"database": ["DB_*"], "secrets": ["*PASSWORD*", "DB_*"]}
    result = tag_keys(["DB_PASSWORD"], rules)
    tags = result.tags["DB_PASSWORD"]
    assert "database" in tags
    assert "secrets" in tags


def test_keys_for_tag(tmp_path):
    rules = {"database": ["DB_*"]}
    result = tag_keys(["DB_HOST", "DB_PORT", "APP_NAME"], rules)
    assert result.keys_for_tag("database") == ["DB_HOST", "DB_PORT"]


def test_all_tags(tmp_path):
    rules = {"database": ["DB_*"], "secrets": ["*SECRET*"]}
    result = tag_keys(["DB_HOST", "MY_SECRET"], rules)
    assert result.all_tags() == ["database", "secrets"]


def test_tag_env(tmp_path):
    rules = {"app": ["APP_*"]}
    env = {"APP_NAME": "myapp", "DB_HOST": "localhost"}
    result = tag_env(env, rules)
    assert "APP_NAME" in result.tags
    assert "DB_HOST" not in result.tags


def test_unmatched_key_not_in_tags(tmp_path):
    rules = {"database": ["DB_*"]}
    result = tag_keys(["UNRELATED"], rules)
    assert result.tags == {}
