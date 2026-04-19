"""Tests for envdiff.scoper."""
import pytest
from envdiff.scoper import extract_scope, list_scopes, format_scope_result


ENV = {
    "DB_HOST": "localhost",
    "DB_PORT": "5432",
    "APP_NAME": "envdiff",
    "APP_DEBUG": "true",
    "SECRET_KEY": "abc123",
}


def test_extract_scope_matched_keys():
    result = extract_scope(ENV, "DB")
    assert set(result.matched.keys()) == {"DB_HOST", "DB_PORT"}


def test_extract_scope_strip_prefix():
    result = extract_scope(ENV, "DB", strip_prefix=True)
    assert "HOST" in result.stripped
    assert "PORT" in result.stripped


def test_extract_scope_no_strip():
    result = extract_scope(ENV, "DB", strip_prefix=False)
    assert "DB_HOST" in result.stripped


def test_extract_scope_case_insensitive():
    result = extract_scope(ENV, "app")
    assert set(result.matched.keys()) == {"APP_NAME", "APP_DEBUG"}


def test_extract_scope_no_match():
    result = extract_scope(ENV, "REDIS")
    assert result.matched == {}
    assert result.stripped == {}


def test_extract_scope_no_partial_match():
    # "DB" should not match "DB_HOST" prefix check but NOT a key like "DBMS_X"
    env = {"DBMS_VERSION": "14", "DB_HOST": "localhost"}
    result = extract_scope(env, "DB")
    assert "DB_HOST" in result.matched
    assert "DBMS_VERSION" not in result.matched


def test_list_scopes_returns_sorted():
    scopes = list_scopes(ENV)
    assert scopes == ["APP", "DB", "SECRET"]


def test_list_scopes_empty():
    assert list_scopes({}) == []


def test_list_scopes_no_prefix_keys():
    assert list_scopes({"NODOT": "val"}) == []


def test_format_scope_result_contains_scope_name():
    result = extract_scope(ENV, "DB")
    output = format_scope_result(result)
    assert "DB" in output


def test_format_scope_result_no_match_message():
    result = extract_scope(ENV, "REDIS")
    output = format_scope_result(result)
    assert "no keys matched" in output


def test_format_scope_result_show_original():
    result = extract_scope(ENV, "DB")
    output = format_scope_result(result, show_original=True)
    assert "DB_HOST" in output


def test_format_scope_result_stripped_keys():
    result = extract_scope(ENV, "DB")
    output = format_scope_result(result, show_original=False)
    assert "HOST" in output
    assert "PORT" in output
