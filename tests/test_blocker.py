import os
import pytest
from envdiff.blocker import BlockRule, check_env, load_block_rules
from envdiff.block_formatter import format_block_result, format_block_summary


def _write(tmp_path, name, content):
    p = tmp_path / name
    p.write_text(content)
    return str(p)


def test_no_violations_when_keys_present(tmp_path):
    env = _write(tmp_path, ".env", "DB_URL=postgres://localhost/db\n")
    rules = [BlockRule(key="DB_URL", reason="required")]
    result = check_env(env, rules)
    assert not result.is_blocked
    assert result.violations == []


def test_missing_key_causes_violation(tmp_path):
    env = _write(tmp_path, ".env", "OTHER=value\n")
    rules = [BlockRule(key="DB_URL", reason="must be configured")]
    result = check_env(env, rules)
    assert result.is_blocked
    assert any("DB_URL" in v for v in result.violations)


def test_empty_value_causes_violation(tmp_path):
    env = _write(tmp_path, ".env", "SECRET_KEY=\n")
    rules = [BlockRule(key="SECRET_KEY", reason="cannot be empty")]
    result = check_env(env, rules)
    assert result.is_blocked


def test_forbidden_value_causes_violation(tmp_path):
    env = _write(tmp_path, ".env", "ENV=development\n")
    rules = [BlockRule(key="ENV", reason="not for prod", forbidden_values=["development", "test"])]
    result = check_env(env, rules)
    assert result.is_blocked
    assert any("forbidden" in v for v in result.violations)


def test_allowed_value_passes(tmp_path):
    env = _write(tmp_path, ".env", "ENV=production\n")
    rules = [BlockRule(key="ENV", reason="not for prod", forbidden_values=["development"])]
    result = check_env(env, rules)
    assert not result.is_blocked


def test_load_block_rules(tmp_path):
    rules_file = _write(tmp_path, ".blockrules",
        "# comment\nDB_URL # must be set\nENV forbidden=development,test # env check\n")
    rules = load_block_rules(rules_file)
    assert len(rules) == 2
    assert rules[0].key == "DB_URL"
    assert rules[1].forbidden_values == ["development", "test"]


def test_format_block_result_blocked(tmp_path):
    env = _write(tmp_path, ".env", "X=1\n")
    rules = [BlockRule(key="MISSING", reason="needed")]
    result = check_env(env, rules)
    output = format_block_result(result, color=False)
    assert "BLOCKED" in output
    assert "MISSING" in output


def test_format_block_result_ok(tmp_path):
    env = _write(tmp_path, ".env", "KEY=value\n")
    rules = [BlockRule(key="KEY", reason="")]
    result = check_env(env, rules)
    output = format_block_result(result, color=False)
    assert "OK" in output


def test_format_block_summary(tmp_path):
    env1 = _write(tmp_path, "a.env", "KEY=val\n")
    env2 = _write(tmp_path, "b.env", "OTHER=x\n")
    rules = [BlockRule(key="KEY", reason="")]
    results = [check_env(env1, rules), check_env(env2, rules)]
    summary = format_block_summary(results, color=False)
    assert "1/2" in summary
