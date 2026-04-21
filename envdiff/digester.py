"""Digest module: compute and compare checksums for .env files."""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List

from envdiff.parser import parse_env_file


@dataclass
class DigestEntry:
    path: str
    checksum: str  # sha256 hex digest of sorted key=value pairs
    key_count: int


@dataclass
class DigestResult:
    entries: List[DigestEntry] = field(default_factory=list)
    conflicts: List[str] = field(default_factory=list)  # paths whose checksums differ


def _checksum(env: Dict[str, str]) -> str:
    """Return a deterministic SHA-256 hex digest for an env mapping."""
    canonical = "\n".join(f"{k}={v}" for k, v in sorted(env.items()))
    return hashlib.sha256(canonical.encode()).hexdigest()


def digest_file(path: str | Path) -> DigestEntry:
    """Parse *path* and return a DigestEntry with its checksum."""
    env = parse_env_file(str(path))
    return DigestEntry(
        path=str(path),
        checksum=_checksum(env),
        key_count=len(env),
    )


def digest_many(paths: List[str | Path]) -> DigestResult:
    """Digest all *paths* and flag any whose checksum differs from the first."""
    entries = [digest_file(p) for p in paths]
    reference = entries[0].checksum if entries else None
    conflicts = [
        e.path for e in entries[1:] if e.checksum != reference
    ]
    return DigestResult(entries=entries, conflicts=conflicts)


def save_digest(result: DigestResult, dest: str | Path) -> None:
    """Persist digest entries to a JSON file at *dest*."""
    dest = Path(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    payload = [
        {"path": e.path, "checksum": e.checksum, "key_count": e.key_count}
        for e in result.entries
    ]
    dest.write_text(json.dumps(payload, indent=2))


def load_digest(src: str | Path) -> DigestResult:
    """Load a previously saved digest JSON and return a DigestResult."""
    raw = json.loads(Path(src).read_text())
    entries = [
        DigestEntry(path=r["path"], checksum=r["checksum"], key_count=r["key_count"])
        for r in raw
    ]
    reference = entries[0].checksum if entries else None
    conflicts = [e.path for e in entries[1:] if e.checksum != reference]
    return DigestResult(entries=entries, conflicts=conflicts)
