"""Tests for envdiff.encryptor."""
import pytest
from envdiff.encryptor import (
    encrypt_env,
    decrypt_env,
    is_encrypted,
    _xor_encrypt,
    _xor_decrypt,
    _derive_key,
)

PASSWORD = "s3cr3t"


def _key():
    return _derive_key(PASSWORD)


def test_is_encrypted_true():
    token = _xor_encrypt("hello", _key())
    assert is_encrypted(token)


def test_is_encrypted_false():
    assert not is_encrypted("plainvalue")


def test_round_trip():
    token = _xor_encrypt("my_password_123", _key())
    assert _xor_decrypt(token, _key()) == "my_password_123"


def test_encrypt_env_sensitive_key():
    env = {"DB_PASSWORD": "secret", "APP_NAME": "myapp"}
    result = encrypt_env(env, PASSWORD)
    assert is_encrypted(result.encrypted["DB_PASSWORD"])
    assert result.encrypted["APP_NAME"] == "myapp"
    assert "APP_NAME" in result.skipped


def test_encrypt_env_all_keys():
    env = {"APP_NAME": "myapp", "PORT": "8080"}
    result = encrypt_env(env, PASSWORD, all_keys=True)
    assert is_encrypted(result.encrypted["APP_NAME"])
    assert is_encrypted(result.encrypted["PORT"])
    assert result.skipped == []


def test_encrypt_env_already_encrypted():
    token = _xor_encrypt("value", _key())
    env = {"API_KEY": token}
    result = encrypt_env(env, PASSWORD)
    assert "API_KEY" in result.already_encrypted
    assert result.encrypted["API_KEY"] == token


def test_decrypt_env():
    env = {"DB_PASSWORD": "secret", "APP_NAME": "myapp"}
    encrypted = encrypt_env(env, PASSWORD).encrypted
    decrypted = decrypt_env(encrypted, PASSWORD)
    assert decrypted["DB_PASSWORD"] == "secret"
    assert decrypted["APP_NAME"] == "myapp"


def test_decrypt_plain_passthrough():
    env = {"PLAIN": "value"}
    assert decrypt_env(env, PASSWORD) == {"PLAIN": "value"}


def test_wrong_password_gives_garbage():
    token = _xor_encrypt("secret", _key())
    wrong_key = _derive_key("wrongpass")
    result = _xor_decrypt(token, wrong_key)
    assert result != "secret"
