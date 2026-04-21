"""Tests for envdiff.rule_checker."""
import pytest

from envdiff.rule_checker import (
    RuleCheckResult,
    RuleViolation,
    check_rules,
)
from envdiff.linter_rules import DEFAULT_RULES


def _clean_env():
    return {"HOST": "localhost", "PORT": "5432", "DEBUG": "true"}


def test_clean_env_is_clean():
    result = check_rules(_clean_env())
    assert result.is_clean


def test_empty_value_triggers_warning():
    result = check_rules({"API_KEY": ""})
    assert not result.is_clean
    assert any(v.rule_name == "empty-value" for v in result.warnings)


def test_spaces_in_key_triggers_error():
    result = check_rules({"MY KEY": "value"})
    errors = [v for v in result.errors if v.rule_name == "spaces-in-key"]
    assert len(errors) == 1
    assert errors[0].key == "MY KEY"


def test_key_starts_with_digit_triggers_error():
    result = check_rules({"1BAD": "val"})
    errors = [v for v in result.errors if v.rule_name == "key-starts-with-digit"]
    assert len(errors) == 1


def test_unquoted_spaces_in_value_warning():
    result = check_rules({"GREETING": "hello world"})
    warnings = [v for v in result.warnings if v.rule_name == "unquoted-spaces-in-value"]
    assert len(warnings) == 1


def test_skip_rule_suppresses_violation():
    result = check_rules({"API_KEY": ""}, skip=["empty-value"])
    assert all(v.rule_name != "empty-value" for v in result.violations)


def test_multiple_violations_collected():
    env = {"MY KEY": "", "1NUM": "hello world"}
    result = check_rules(env)
    assert len(result.violations) >= 3


def test_errors_property_filters_correctly():
    result = check_rules({"MY KEY": "value"})
    assert all(v.severity == "error" for v in result.errors)


def test_warnings_property_filters_correctly():
    result = check_rules({"EMPTY": ""})
    assert all(v.severity == "warning" for v in result.warnings)


def test_violation_str_contains_key_and_rule():
    v = RuleViolation(rule_name="empty-value", severity="warning", key="FOO", description="desc")
    s = str(v)
    assert "FOO" in s
    assert "empty-value" in s
