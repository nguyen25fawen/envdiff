"""Tests for envdiff.masked_diff."""
import pytest
from envdiff.masked_diff import build_masked_diff, MaskedDiffEntry


BASE = {
    "APP_NAME": "myapp",
    "DB_PASSWORD": "s3cr3t",
    "API_KEY": "abc123",
    "PORT": "8080",
}

TARGET = {
    "APP_NAME": "myapp",
    "DB_PASSWORD": "different",
    "PORT": "9090",
    "NEW_KEY": "hello",
}


def test_has_differences_when_keys_differ():
    result = build_masked_diff(BASE, TARGET)
    assert result.has_differences()


def test_no_differences_when_identical():
    env = {"A": "1", "B": "2"}
    result = build_masked_diff(env, env.copy())
    assert not result.has_differences()


def test_missing_in_target_detected():
    result = build_masked_diff(BASE, TARGET)
    missing = result.by_kind("missing_in_target")
    assert any(e.key == "API_KEY" for e in missing)


def test_missing_in_base_detected():
    result = build_masked_diff(BASE, TARGET)
    missing = result.by_kind("missing_in_base")
    assert any(e.key == "NEW_KEY" for e in missing)


def test_mismatch_detected():
    result = build_masked_diff(BASE, TARGET, check_values=True)
    mismatches = result.by_kind("mismatch")
    keys = [e.key for e in mismatches]
    assert "PORT" in keys


def test_sensitive_password_is_redacted():
    result = build_masked_diff(BASE, TARGET, check_values=True)
    entry = next(e for e in result.entries if e.key == "DB_PASSWORD")
    assert entry.is_sensitive
    assert entry.base_value == "***"
    assert entry.target_value == "***"


def test_sensitive_api_key_is_redacted():
    result = build_masked_diff(BASE, TARGET)
    entry = next(e for e in result.entries if e.key == "API_KEY")
    assert entry.is_sensitive
    assert entry.base_value == "***"


def test_non_sensitive_value_visible():
    result = build_masked_diff(BASE, TARGET)
    entry = next(e for e in result.entries if e.key == "APP_NAME")
    assert not entry.is_sensitive
    assert entry.base_value == "myapp"


def test_labels_stored():
    result = build_masked_diff(BASE, TARGET, base_label="prod", target_label="staging")
    assert result.base_label == "prod"
    assert result.target_label == "staging"


def test_check_values_false_skips_mismatches():
    result = build_masked_diff(BASE, TARGET, check_values=False)
    assert not result.by_kind("mismatch")


def test_equal_entries_present():
    result = build_masked_diff(BASE, TARGET)
    equal = result.by_kind("equal")
    assert any(e.key == "APP_NAME" for e in equal)


def test_missing_in_target_base_value_set():
    result = build_masked_diff(BASE, TARGET)
    entry = next(e for e in result.entries if e.key == "API_KEY")
    assert entry.target_value is None
    assert entry.base_value == "***"  # API_KEY is sensitive
