"""Tests for envdiff.differ_whitelist."""
from __future__ import annotations

from pathlib import Path

import pytest

from envdiff.comparator import DiffResult
from envdiff.differ_whitelist import (
    WhitelistResult,
    apply_whitelist,
    load_whitelist,
)


def _diff(
    missing_second=None,
    missing_first=None,
    mismatched=None,
) -> DiffResult:
    return DiffResult(
        missing_in_second=missing_second or [],
        missing_in_first=missing_first or [],
        mismatched=mismatched or [],
    )


def _write(tmp_path: Path, content: str) -> Path:
    p = tmp_path / ".envwhitelist"
    p.write_text(content)
    return p


# --- load_whitelist ---

def test_load_whitelist_basic(tmp_path):
    p = _write(tmp_path, "DB_*\nAPI_KEY\n")
    patterns = load_whitelist(p)
    assert patterns == ["DB_*", "API_KEY"]


def test_load_whitelist_skips_comments(tmp_path):
    p = _write(tmp_path, "# ignore me\nDB_HOST\n")
    patterns = load_whitelist(p)
    assert patterns == ["DB_HOST"]


def test_load_whitelist_skips_blank_lines(tmp_path):
    p = _write(tmp_path, "\nDB_HOST\n\n")
    patterns = load_whitelist(p)
    assert patterns == ["DB_HOST"]


# --- apply_whitelist ---

def test_only_matching_keys_included():
    diff = _diff(missing_second=["DB_HOST", "UNRELATED_KEY"])
    result = apply_whitelist(diff, ["DB_*"])
    assert result.missing_in_second == ["DB_HOST"]
    assert "UNRELATED_KEY" not in result.missing_in_second


def test_no_patterns_returns_empty_result():
    diff = _diff(missing_second=["DB_HOST", "API_KEY"], mismatched=["SECRET"])
    result = apply_whitelist(diff, [])
    assert result.is_empty()


def test_glob_wildcard_matches_multiple_keys():
    diff = _diff(missing_second=["DB_HOST", "DB_PORT", "REDIS_URL"])
    result = apply_whitelist(diff, ["DB_*"])
    assert set(result.missing_in_second) == {"DB_HOST", "DB_PORT"}


def test_exact_match_pattern():
    diff = _diff(mismatched=["API_KEY", "OTHER"])
    result = apply_whitelist(diff, ["API_KEY"])
    assert result.mismatched == ["API_KEY"]


def test_missing_in_first_filtered():
    diff = _diff(missing_first=["TOKEN", "EXTRA"])
    result = apply_whitelist(diff, ["TOKEN"])
    assert result.missing_in_first == ["TOKEN"]
    assert "EXTRA" not in result.missing_in_first


def test_is_empty_when_no_matches():
    diff = _diff(missing_second=["UNRELATED"])
    result = apply_whitelist(diff, ["DB_*"])
    assert result.is_empty()


def test_pair_label_stored():
    diff = _diff()
    result = apply_whitelist(diff, ["*"], pair_label="prod vs staging")
    assert result.pair_label == "prod vs staging"


def test_results_are_sorted():
    diff = _diff(missing_second=["Z_KEY", "A_KEY", "M_KEY"])
    result = apply_whitelist(diff, ["*"])
    assert result.missing_in_second == ["A_KEY", "M_KEY", "Z_KEY"]


def test_by_kind_returns_correct_list():
    diff = _diff(missing_second=["DB_HOST"], mismatched=["API_KEY"])
    result = apply_whitelist(diff, ["*"])
    assert result.by_kind("missing_in_second") == ["DB_HOST"]
    assert result.by_kind("mismatched") == ["API_KEY"]
    assert result.by_kind("unknown") == []
