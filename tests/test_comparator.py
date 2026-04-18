"""Tests for envdiff.comparator."""

import pytest
from envdiff.comparator import compare_envs, DiffResult


ENV_A = {"HOST": "localhost", "PORT": "5432", "DEBUG": "true"}
ENV_B = {"HOST": "prod.example.com", "PORT": "5432", "SECRET": "abc123"}


def test_missing_in_second():
    result = compare_envs(ENV_A, ENV_B)
    assert "DEBUG" in result.missing_in_second
    assert "SECRET" not in result.missing_in_second


def test_missing_in_first():
    result = compare_envs(ENV_A, ENV_B)
    assert "SECRET" in result.missing_in_first
    assert "DEBUG" not in result.missing_in_first


def test_value_mismatch_detected():
    result = compare_envs(ENV_A, ENV_B)
    assert "HOST" in result.value_mismatches
    assert result.value_mismatches["HOST"] == ("localhost", "prod.example.com")


def test_no_mismatch_for_equal_values():
    result = compare_envs(ENV_A, ENV_B)
    assert "PORT" not in result.value_mismatches


def test_check_values_false_skips_mismatches():
    result = compare_envs(ENV_A, ENV_B, check_values=False)
    assert result.value_mismatches == {}


def test_identical_envs_no_differences():
    result = compare_envs(ENV_A, ENV_A)
    assert not result.has_differences


def test_empty_envs():
    result = compare_envs({}, {})
    assert not result.has_differences


def test_one_empty_env():
    result = compare_envs(ENV_A, {})
    assert set(result.missing_in_second) == set(ENV_A.keys())
    assert result.missing_in_first == []
