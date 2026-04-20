import pytest
from envdiff.flattener import (
    flatten_env,
    format_flatten_result,
    any_renamed,
    FlattenResult,
)


def test_clean_keys_unchanged():
    env = {"APP_HOST": "localhost", "APP_PORT": "5432"}
    result = flatten_env(env)
    assert result.flattened == env
    assert result.renamed == {}


def test_double_separator_collapsed():
    env = {"APP__HOST": "localhost"}
    result = flatten_env(env, separator="__")
    assert "APP_HOST" in result.flattened
    assert result.renamed["APP__HOST"] == "APP_HOST"


def test_triple_separator_collapsed():
    env = {"APP___HOST": "val"}
    result = flatten_env(env, separator="__")
    assert "APP_HOST" in result.flattened


def test_leading_separator_stripped():
    env = {"__APP_HOST": "val"}
    result = flatten_env(env, separator="__")
    assert "APP_HOST" in result.flattened
    assert result.renamed["__APP_HOST"] == "APP_HOST"


def test_trailing_separator_stripped():
    env = {"APP_HOST__": "val"}
    result = flatten_env(env, separator="__")
    assert "APP_HOST" in result.flattened


def test_lowercase_flag():
    env = {"APP_HOST": "localhost"}
    result = flatten_env(env, lowercase=True)
    assert "app_host" in result.flattened
    assert result.renamed["APP_HOST"] == "app_host"


def test_any_renamed_true():
    env = {"APP__HOST": "x"}
    result = flatten_env(env)
    assert any_renamed(result) is True


def test_any_renamed_false():
    env = {"APP_HOST": "x"}
    result = flatten_env(env)
    assert any_renamed(result) is False


def test_original_preserved():
    env = {"APP__HOST": "val"}
    result = flatten_env(env)
    assert result.original == env


def test_format_no_renames():
    env = {"KEY": "val"}
    result = flatten_env(env)
    out = format_flatten_result(result)
    assert "No keys were renamed" in out


def test_format_shows_renames():
    env = {"APP__HOST": "val"}
    result = flatten_env(env)
    out = format_flatten_result(result)
    assert "APP__HOST" in out
    assert "APP_HOST" in out
    assert "->" in out


def test_format_show_unchanged():
    env = {"APP__HOST": "val", "CLEAN_KEY": "x"}
    result = flatten_env(env)
    out = format_flatten_result(result, show_unchanged=True)
    assert "CLEAN_KEY" in out
