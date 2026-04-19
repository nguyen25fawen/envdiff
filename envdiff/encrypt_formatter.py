"""Format output for encrypt/decrypt operations."""
from __future__ import annotations

from typing import List

from envdiff.encryptor import EncryptResult


def _c(text: str, code: str) -> str:
    return f"\033[{code}m{text}\033[0m"


def format_encrypt_result(result: EncryptResult, *, color: bool = True) -> str:
    lines: List[str] = []

    if result.already_encrypted:
        for k in sorted(result.already_encrypted):
            label = _c("SKIP (already encrypted)", "33") if color else "SKIP (already encrypted)"
            lines.append(f"  {label}  {k}")

    encrypted_keys = [
        k for k in result.encrypted
        if k not in result.skipped and k not in result.already_encrypted
    ]
    for k in sorted(encrypted_keys):
        label = _c("ENCRYPTED", "32") if color else "ENCRYPTED"
        lines.append(f"  {label}  {k}")

    for k in sorted(result.skipped):
        label = _c("plain", "2") if color else "plain"
        lines.append(f"  {label}     {k}")

    if not lines:
        return "No keys processed."
    return "\n".join(lines)


def format_encrypt_summary(result: EncryptResult, *, color: bool = True) -> str:
    n_enc = len(result.encrypted) - len(result.skipped) - len(result.already_encrypted)
    parts = [f"{n_enc} encrypted", f"{len(result.skipped)} plain", f"{len(result.already_encrypted)} skipped"]
    summary = ", ".join(parts)
    return (_c(summary, "1") if color else summary)
