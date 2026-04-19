"""Tests for envdiff.differ_filter."""
import pytest
from envdiff.differ import EnvDiff, MultiDiff
from envdiff.differ_filter import (
    filter_by_keys,
    filter_multi_by_keys,
    keep_only_missing,
    keep_only_mismatched,
    severity_filter,
)


def _diff() -> EnvDiff:
    return EnvDiff(
        missing_in_target={"DB_HOST": "localhost", "DB_PORT": "5432"},
        missing_in_base={"NEW_KEY": "val"},
        mismatched={"APP_ENV": ("dev", "prod"), "LOG_LEVEL": ("debug", "info")},
    )


def test_filter_by_keys_exact():
    result = filter_by_keys(_diff(), ["DB_HOST"])
    assert "DB_HOST" in result.missing_in_target
    assert "DB_PORT" not in result.missing_in_target


def test_filter_by_keys_glob():
    result = filter_by_keys(_diff(), ["DB_*"])
    assert set(result.missing_in_target.keys()) == {"DB_HOST", "DB_PORT"}


def test_filter_by_keys_removes_mismatched():
    result = filter_by_keys(_diff(), ["APP_ENV"])
    assert "APP_ENV" in result.mismatched
    assert "LOG_LEVEL" not in result.mismatched


def test_filter_by_keys_no_match():
    result = filter_by_keys(_diff(), ["UNKNOWN_*"])
    assert not result.missing_in_target
    assert not result.missing_in_base
    assert not result.mismatched


def test_filter_multi_by_keys():
    multi = MultiDiff(base="base.env", diffs={"prod": _diff(), "staging": _diff()})
    result = filter_multi_by_keys(multi, ["APP_ENV"])
    for d in result.diffs.values():
        assert "APP_ENV" in d.mismatched
        assert not d.missing_in_target


def test_keep_only_missing():
    result = keep_only_missing(_diff())
    assert result.missing_in_target
    assert result.missing_in_base
    assert not result.mismatched


def test_keep_only_mismatched():
    result = keep_only_mismatched(_diff())
    assert result.mismatched
    assert not result.missing_in_target
    assert not result.missing_in_base


def test_severity_filter_missing():
    result = severity_filter(_diff(), "missing")
    assert not result.mismatched


def test_severity_filter_mismatch():
    result = severity_filter(_diff(), "mismatch")
    assert not result.missing_in_target
    assert not result.missing_in_base


def test_severity_filter_all():
    result = severity_filter(_diff(), "all")
    assert result.mismatched
    assert result.missing_in_target
