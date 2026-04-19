"""Tests for envdiff.classifier."""
import pytest
from envdiff.classifier import classify_value, classify_env, format_classification, ClassifiedEnv


def test_classify_url():
    assert classify_value("https://example.com") == "url"


def test_classify_http_url():
    assert classify_value("http://localhost:8080") == "url"


def test_classify_path():
    assert classify_value("/var/log/app.log") == "path"


def test_classify_integer():
    assert classify_value("42") == "integer"


def test_classify_negative_integer():
    assert classify_value("-7") == "integer"


def test_classify_float():
    assert classify_value("3.14") == "float"


def test_classify_boolean_true():
    assert classify_value("true") == "boolean"


def test_classify_boolean_yes():
    assert classify_value("yes") == "boolean"


def test_classify_boolean_zero():
    assert classify_value("0") == "boolean"


def test_classify_uuid():
    assert classify_value("123e4567-e89b-12d3-a456-426614174000") == "uuid"


def test_classify_empty():
    assert classify_value("") == "empty"


def test_classify_string_fallback():
    assert classify_value("my-app-name") == "string"


def test_classify_env_returns_all_keys():
    env = {"PORT": "8080", "DATABASE_URL": "postgres://localhost/db", "DEBUG": "true"}
    result = classify_env(".env", env)
    assert result.path == ".env"
    assert result.types["PORT"] == "integer"
    assert result.types["DATABASE_URL"] == "url"
    assert result.types["DEBUG"] == "boolean"


def test_classify_env_empty():
    result = classify_env(".env", {})
    assert result.types == {}


def test_format_classification_basic():
    classified = ClassifiedEnv(path=".env", types={"PORT": "integer", "NAME": "string"})
    output = format_classification(classified)
    assert ".env" in output
    assert "PORT: integer" in output
    assert "NAME: string" in output


def test_format_classification_empty():
    classified = ClassifiedEnv(path=".env.test", types={})
    output = format_classification(classified)
    assert "(no keys)" in output
