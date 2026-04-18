"""Tests for envdiff.redactor."""

import pytest
from envdiff.redactor import redact, redact_many, is_sensitive, REDACTED, _compile


def test_password_key_is_redacted():
    result = redact({"DB_PASSWORD": "hunter2"})
    assert result["DB_PASSWORD"] == REDACTED


def test_secret_key_is_redacted():
    result = redact({"APP_SECRET": "abc123"})
    assert result["APP_SECRET"] == REDACTED


def test_token_key_is_redacted():
    result = redact({"GITHUB_TOKEN": "ghp_xyz"})
    assert result["GITHUB_TOKEN"] == REDACTED


def test_api_key_is_redacted():
    result = redact({"STRIPE_API_KEY": "sk_live_abc"})
    assert result["STRIPE_API_KEY"] == REDACTED


def test_safe_key_is_not_redacted():
    result = redact({"APP_ENV": "production"})
    assert result["APP_ENV"] == "production"


def test_multiple_keys_mixed():
    env = {"HOST": "localhost", "DB_PASSWORD": "secret", "PORT": "5432"}
    result = redact(env)
    assert result["HOST"] == "localhost"
    assert result["PORT"] == "5432"
    assert result["DB_PASSWORD"] == REDACTED


def test_custom_placeholder():
    result = redact({"AUTH_TOKEN": "xyz"}, placeholder="[hidden]")
    assert result["AUTH_TOKEN"] == "[hidden]"


def test_extra_patterns():
    result = redact({"MY_INTERNAL_KEY": "value"}, extra_patterns=[r"(?i)internal"])
    assert result["MY_INTERNAL_KEY"] == REDACTED


def test_extra_patterns_do_not_affect_safe_keys():
    result = redact({"APP_NAME": "envdiff"}, extra_patterns=[r"(?i)internal"])
    assert result["APP_NAME"] == "envdiff"


def test_is_sensitive_true():
    compiled = _compile([r"(?i)password"])
    assert is_sensitive("DB_PASSWORD", compiled) is True


def test_is_sensitive_false():
    compiled = _compile([r"(?i)password"])
    assert is_sensitive("APP_NAME", compiled) is False


def test_redact_many():
    envs = {
        "staging": {"HOST": "stg.example.com", "DB_PASSWORD": "stg_pass"},
        "prod": {"HOST": "prod.example.com", "DB_PASSWORD": "prod_pass"},
    }
    result = redact_many(envs)
    assert result["staging"]["HOST"] == "stg.example.com"
    assert result["staging"]["DB_PASSWORD"] == REDACTED
    assert result["prod"]["HOST"] == "prod.example.com"
    assert result["prod"]["DB_PASSWORD"] == REDACTED


def test_redact_empty_env():
    assert redact({}) == {}
