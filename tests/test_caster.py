import pytest
from envdiff.caster import cast_value, infer_type, cast_env, format_cast_result, CastResult


def test_cast_true_variants():
    for v in ("true", "True", "TRUE", "yes", "1", "on"):
        assert cast_value(v) is True


def test_cast_false_variants():
    for v in ("false", "False", "no", "0", "off"):
        assert cast_value(v) is False


def test_cast_integer():
    assert cast_value("42") == 42
    assert isinstance(cast_value("42"), int)


def test_cast_negative_integer():
    assert cast_value("-7") == -7


def test_cast_float():
    result = cast_value("3.14")
    assert abs(result - 3.14) < 1e-9
    assert isinstance(result, float)


def test_cast_string_unchanged():
    assert cast_value("hello") == "hello"
    assert isinstance(cast_value("hello"), str)


def test_infer_type_bool():
    assert infer_type("true") == "bool"
    assert infer_type("no") == "bool"


def test_infer_type_int():
    assert infer_type("100") == "int"


def test_infer_type_float():
    assert infer_type("1.5") == "float"


def test_infer_type_str():
    assert infer_type("postgres://localhost/db") == "str"


def test_cast_env_returns_cast_result():
    env = {"DEBUG": "true", "PORT": "8080", "NAME": "app"}
    result = cast_env(env)
    assert isinstance(result, CastResult)
    assert result.casted["DEBUG"] is True
    assert result.casted["PORT"] == 8080
    assert result.casted["NAME"] == "app"


def test_cast_env_types():
    env = {"ENABLED": "false", "TIMEOUT": "30", "RATIO": "0.5"}
    result = cast_env(env)
    assert result.types["ENABLED"] == "bool"
    assert result.types["TIMEOUT"] == "int"
    assert result.types["RATIO"] == "float"


def test_format_cast_result_no_values():
    env = {"PORT": "8080"}
    result = cast_env(env)
    output = format_cast_result(result)
    assert "PORT" in output
    assert "int" in output
    assert "8080" not in output


def test_format_cast_result_with_values():
    env = {"PORT": "8080"}
    result = cast_env(env)
    output = format_cast_result(result, show_values=True)
    assert "8080" in output


def test_format_cast_result_empty():
    result = cast_env({})
    assert format_cast_result(result) == "No keys to cast."
