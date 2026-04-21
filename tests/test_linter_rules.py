"""Tests for envdiff.linter_rules."""
import pytest

from envdiff.linter_rules import (
    DEFAULT_RULES,
    rule_by_name,
    rules_by_severity,
    _is_empty_value,
    _has_spaces_in_key,
    _value_has_unquoted_spaces,
    _key_starts_with_digit,
    _is_whitespace_key,
)


def test_default_rules_not_empty():
    assert len(DEFAULT_RULES) > 0


def test_all_rules_have_name_and_severity():
    for rule in DEFAULT_RULES:
        assert rule.name
        assert rule.severity in ("error", "warning")


def test_rule_by_name_found():
    rule = rule_by_name("empty-value")
    assert rule is not None
    assert rule.name == "empty-value"


def test_rule_by_name_missing_returns_none():
    assert rule_by_name("nonexistent-rule") is None


def test_rules_by_severity_errors():
    errors = rules_by_severity("error")
    assert all(r.severity == "error" for r in errors)


def test_rules_by_severity_warnings():
    warnings = rules_by_severity("warning")
    assert all(r.severity == "warning" for r in warnings)


def test_is_empty_value_true():
    assert _is_empty_value("KEY", "") is True
    assert _is_empty_value("KEY", "   ") is True


def test_is_empty_value_false():
    assert _is_empty_value("KEY", "value") is False


def test_has_spaces_in_key_true():
    assert _has_spaces_in_key("MY KEY", "val") is True


def test_has_spaces_in_key_false():
    assert _has_spaces_in_key("MY_KEY", "val") is False


def test_value_has_unquoted_spaces_true():
    assert _value_has_unquoted_spaces("K", "hello world") is True


def test_value_has_unquoted_spaces_quoted_ok():
    assert _value_has_unquoted_spaces("K", "'hello world'") is False
    assert _value_has_unquoted_spaces("K", '"hello world"') is False


def test_key_starts_with_digit_true():
    assert _key_starts_with_digit("1KEY", "v") is True


def test_key_starts_with_digit_false():
    assert _key_starts_with_digit("KEY1", "v") is False


def test_whitespace_key_true():
    assert _is_whitespace_key(" KEY", "v") is True
    assert _is_whitespace_key("KEY ", "v") is True


def test_whitespace_key_false():
    assert _is_whitespace_key("KEY", "v") is False
