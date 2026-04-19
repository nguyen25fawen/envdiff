from envdiff.caster import cast_env
from envdiff.cast_formatter import format_cast_rich, format_cast_summary


def _result(env: dict):
    return cast_env(env)


def test_empty_env_message():
    r = _result({})
    out = format_cast_rich(r)
    assert "No keys to cast" in out


def test_header_shown():
    r = _result({"PORT": "8080"})
    out = format_cast_rich(r)
    assert "Type inference" in out


def test_key_appears_in_output():
    r = _result({"DEBUG": "true", "PORT": "8080"})
    out = format_cast_rich(r)
    assert "DEBUG" in out
    assert "PORT" in out


def test_type_label_shown():
    r = _result({"DEBUG": "true"})
    out = format_cast_rich(r)
    assert "bool" in out


def test_value_hidden_by_default():
    r = _result({"PORT": "8080"})
    out = format_cast_rich(r)
    assert "8080" not in out


def test_value_shown_when_flag_set():
    r = _result({"PORT": "8080"})
    out = format_cast_rich(r, show_values=True)
    assert "8080" in out


def test_summary_contains_total():
    r = _result({"A": "1", "B": "hello", "C": "true"})
    s = format_cast_summary(r)
    assert "3 keys" in s


def test_summary_type_counts():
    r = _result({"A": "1", "B": "2", "C": "hello"})
    s = format_cast_summary(r)
    assert "int=2" in s
    assert "str=1" in s


def test_summary_empty():
    r = _result({})
    s = format_cast_summary(r)
    assert "0 keys" in s
