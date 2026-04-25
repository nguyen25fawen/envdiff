"""Tests for differ_changelog and changelog_formatter."""
import pytest

from envdiff.differ_changelog import build_changelog, ChangelogEntry
from envdiff.changelog_formatter import format_changelog_rich, format_changelog_summary


BASE = {"DB_HOST": "localhost", "DB_PORT": "5432", "SECRET": "abc"}
TARGET = {"DB_HOST": "prod.db", "DB_PORT": "5432", "API_KEY": "xyz"}


def test_added_key_detected():
    result = build_changelog(BASE, TARGET)
    added = result.by_kind("added")
    assert any(e.key == "API_KEY" for e in added)


def test_removed_key_detected():
    result = build_changelog(BASE, TARGET)
    removed = result.by_kind("removed")
    assert any(e.key == "SECRET" for e in removed)


def test_changed_value_detected():
    result = build_changelog(BASE, TARGET)
    changed = result.by_kind("changed")
    assert any(e.key == "DB_HOST" for e in changed)


def test_unchanged_key_not_in_entries():
    result = build_changelog(BASE, TARGET)
    keys = [e.key for e in result.entries]
    assert "DB_PORT" not in keys


def test_is_empty_when_identical():
    env = {"A": "1", "B": "2"}
    result = build_changelog(env, env)
    assert result.is_empty()


def test_redact_hides_values_by_default():
    result = build_changelog(BASE, TARGET, redact=True)
    for entry in result.entries:
        assert entry.old_value is None
        assert entry.new_value is None


def test_no_redact_exposes_values():
    result = build_changelog(BASE, TARGET, redact=False)
    changed = result.by_kind("changed")
    db_host = next(e for e in changed if e.key == "DB_HOST")
    assert db_host.old_value == "localhost"
    assert db_host.new_value == "prod.db"


def test_labels_stored():
    result = build_changelog(BASE, TARGET, base_label="v1", target_label="v2")
    assert result.base_label == "v1"
    assert result.target_label == "v2"


def test_entries_sorted_alphabetically():
    result = build_changelog(BASE, TARGET)
    keys = [e.key for e in result.entries]
    assert keys == sorted(keys)


def test_format_rich_no_changes():
    env = {"X": "1"}
    result = build_changelog(env, env)
    output = format_changelog_rich(result)
    assert "No changes" in output


def test_format_rich_shows_added_key():
    result = build_changelog(BASE, TARGET)
    output = format_changelog_rich(result)
    assert "API_KEY" in output


def test_format_rich_shows_removed_key():
    result = build_changelog(BASE, TARGET)
    output = format_changelog_rich(result)
    assert "SECRET" in output


def test_format_rich_show_values_flag():
    result = build_changelog(BASE, TARGET, redact=False)
    output = format_changelog_rich(result, show_values=True)
    assert "prod.db" in output


def test_format_summary_no_changes():
    env = {"A": "1"}
    result = build_changelog(env, env)
    summary = format_changelog_summary(result)
    assert "no changes" in summary


def test_format_summary_counts():
    result = build_changelog(BASE, TARGET)
    summary = format_changelog_summary(result)
    assert "added" in summary
    assert "removed" in summary
    assert "changed" in summary
