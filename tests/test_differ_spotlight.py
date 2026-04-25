"""Tests for envdiff.differ_spotlight."""
import pytest

from envdiff.differ_spotlight import (
    SpotlightEntry,
    SpotlightResult,
    _risk_score,
    build_spotlight,
)


# ---------------------------------------------------------------------------
# _risk_score
# ---------------------------------------------------------------------------

def test_risk_score_safe_key_short_value():
    assert _risk_score("APP_NAME", "myapp") == 0


def test_risk_score_sensitive_key_raises_score():
    score = _risk_score("DB_PASSWORD", "short")
    assert score >= 2


def test_risk_score_long_value_adds_one():
    base = _risk_score("PLAIN_KEY", "x" * 32)
    assert base >= 1


def test_risk_score_capped_at_three():
    assert _risk_score("SECRET_TOKEN", "x" * 64) <= 3


# ---------------------------------------------------------------------------
# build_spotlight
# ---------------------------------------------------------------------------

def _envs():
    return {
        "dev.env": {"APP_NAME": "myapp", "DB_PASSWORD": "devpass", "ONLY_DEV": "1"},
        "prod.env": {"APP_NAME": "myapp", "DB_PASSWORD": "prodpass", "ONLY_PROD": "secret_value_xyz"},
    }


def test_shared_keys_excluded():
    result = build_spotlight(_envs(), min_risk=0)
    keys = {e.key for e in result.entries}
    assert "APP_NAME" not in keys
    assert "DB_PASSWORD" not in keys


def test_exclusive_keys_included():
    result = build_spotlight(_envs(), min_risk=0)
    keys = {e.key for e in result.entries}
    assert "ONLY_DEV" in keys
    assert "ONLY_PROD" in keys


def test_min_risk_filters_low_score_keys():
    envs = {
        "a.env": {"PLAIN": "value"},
        "b.env": {"SECRET_TOKEN": "abc123"},
    }
    result = build_spotlight(envs, min_risk=2)
    keys = {e.key for e in result.entries}
    assert "PLAIN" not in keys
    assert "SECRET_TOKEN" in keys


def test_entries_sorted_by_risk_descending():
    result = build_spotlight(_envs(), min_risk=0)
    scores = [e.risk_score for e in result.entries]
    assert scores == sorted(scores, reverse=True)


def test_file_count_recorded():
    result = build_spotlight(_envs())
    assert result.file_count == 2


def test_is_empty_when_no_exclusive_keys():
    envs = {"a.env": {"K": "v"}, "b.env": {"K": "v"}}
    result = build_spotlight(envs, min_risk=0)
    assert result.is_empty()


def test_high_risk_filter():
    envs = {
        "a.env": {"SECRET_TOKEN": "x" * 40},
        "b.env": {"PLAIN": "hello"},
    }
    result = build_spotlight(envs, min_risk=0)
    high = result.high_risk()
    assert any(e.key == "SECRET_TOKEN" for e in high)


def test_source_file_tracked_correctly():
    result = build_spotlight(_envs(), min_risk=0)
    dev_entry = next(e for e in result.entries if e.key == "ONLY_DEV")
    assert dev_entry.source_file == "dev.env"


def test_empty_envs_returns_empty_result():
    result = build_spotlight({}, min_risk=0)
    assert result.is_empty()
    assert result.file_count == 0
