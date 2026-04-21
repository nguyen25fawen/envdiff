"""Tests for aliaser.py and alias_formatter.py."""
from __future__ import annotations

from pathlib import Path

import pytest

from envdiff.aliaser import (
    AliasRule,
    apply_aliases,
    any_renamed,
    load_alias_rules,
)
from envdiff.alias_formatter import format_alias_result, format_alias_summary


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _write(tmp_path: Path, content: str) -> Path:
    p = tmp_path / "aliases.txt"
    p.write_text(content)
    return p


# ---------------------------------------------------------------------------
# load_alias_rules
# ---------------------------------------------------------------------------

def test_load_basic_rule(tmp_path):
    p = _write(tmp_path, "OLD_KEY=NEW_KEY\n")
    rules = load_alias_rules(p)
    assert len(rules) == 1
    assert rules[0].old == "OLD_KEY"
    assert rules[0].new == "NEW_KEY"


def test_load_ignores_comments(tmp_path):
    p = _write(tmp_path, "# comment\nA=B\n")
    rules = load_alias_rules(p)
    assert len(rules) == 1


def test_load_ignores_blank_lines(tmp_path):
    p = _write(tmp_path, "\nA=B\n\n")
    rules = load_alias_rules(p)
    assert len(rules) == 1


def test_load_skips_lines_without_equals(tmp_path):
    p = _write(tmp_path, "NOEQUALS\nA=B\n")
    rules = load_alias_rules(p)
    assert len(rules) == 1


# ---------------------------------------------------------------------------
# apply_aliases
# ---------------------------------------------------------------------------

def test_rename_existing_key():
    env = {"OLD": "value"}
    rules = [AliasRule(old="OLD", new="NEW")]
    out, result = apply_aliases(env, rules)
    assert "NEW" in out
    assert "OLD" not in out
    assert result.renamed == [("OLD", "NEW")]
    assert any_renamed(result)


def test_unknown_old_key_recorded():
    env = {"UNRELATED": "x"}
    rules = [AliasRule(old="MISSING", new="NEW")]
    out, result = apply_aliases(env, rules)
    assert result.unknown == ["MISSING"]
    assert not result.renamed


def test_skip_when_new_key_present():
    env = {"OLD": "a", "NEW": "b"}
    rules = [AliasRule(old="OLD", new="NEW")]
    out, result = apply_aliases(env, rules)
    assert result.already_present == ["NEW"]
    assert out["NEW"] == "b"  # original value preserved


def test_overwrite_flag_replaces_existing():
    env = {"OLD": "a", "NEW": "b"}
    rules = [AliasRule(old="OLD", new="NEW")]
    out, result = apply_aliases(env, rules, overwrite=True)
    assert out["NEW"] == "a"
    assert result.renamed == [("OLD", "NEW")]


# ---------------------------------------------------------------------------
# formatters
# ---------------------------------------------------------------------------

def test_format_no_changes_message():
    from envdiff.aliaser import AliasResult
    result = AliasResult()
    output = format_alias_result(result, color=False)
    assert "No aliases" in output


def test_format_shows_renamed_pair():
    from envdiff.aliaser import AliasResult
    result = AliasResult(renamed=[("OLD", "NEW")])
    output = format_alias_result(result, color=False)
    assert "OLD" in output
    assert "NEW" in output


def test_format_summary_contains_counts():
    from envdiff.aliaser import AliasResult
    result = AliasResult(renamed=[("A", "B")], unknown=["C"])
    summary = format_alias_summary(result, color=False)
    assert "1 renamed" in summary
    assert "1 not found" in summary
