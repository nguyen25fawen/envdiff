"""Encrypt and decrypt sensitive values in .env files."""
from __future__ import annotations

import base64
import hashlib
import os
from dataclasses import dataclass, field
from typing import Dict, List

from envdiff.redactor import is_sensitive

_MARKER = "enc:"


def _derive_key(password: str) -> bytes:
    return hashlib.sha256(password.encode()).digest()


def _xor_encrypt(value: str, key: bytes) -> str:
    data = value.encode()
    out = bytes(b ^ key[i % len(key)] for i, b in enumerate(data))
    return _MARKER + base64.urlsafe_b64encode(out).decode()


def _xor_decrypt(token: str, key: bytes) -> str:
    raw = base64.urlsafe_b64decode(token[len(_MARKER):])
    return bytes(b ^ key[i % len(key)] for i, b in enumerate(raw)).decode()


def is_encrypted(value: str) -> bool:
    return value.startswith(_MARKER)


@dataclass
class EncryptResult:
    encrypted: Dict[str, str] = field(default_factory=dict)
    skipped: List[str] = field(default_factory=list)
    already_encrypted: List[str] = field(default_factory=list)


def encrypt_env(env: Dict[str, str], password: str, all_keys: bool = False) -> EncryptResult:
    key = _derive_key(password)
    result = EncryptResult()
    for k, v in env.items():
        if is_encrypted(v):
            result.already_encrypted.append(k)
            result.encrypted[k] = v
        elif all_keys or is_sensitive(k):
            result.encrypted[k] = _xor_encrypt(v, key)
        else:
            result.skipped.append(k)
            result.encrypted[k] = v
    return result


def decrypt_env(env: Dict[str, str], password: str) -> Dict[str, str]:
    key = _derive_key(password)
    out: Dict[str, str] = {}
    for k, v in env.items():
        out[k] = _xor_decrypt(v, key) if is_encrypted(v) else v
    return out
