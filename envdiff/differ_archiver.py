"""Archiver: snapshot multiple env files into a dated archive bundle."""
from __future__ import annotations

import json
import hashlib
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

from envdiff.parser import parse_env_file


@dataclass
class ArchiveEntry:
    path: str
    key_count: int
    checksum: str
    keys: List[str]


@dataclass
class ArchiveResult:
    label: str
    created_at: str
    entries: List[ArchiveEntry] = field(default_factory=list)

    @property
    def total_files(self) -> int:
        return len(self.entries)

    @property
    def total_keys(self) -> int:
        return sum(e.key_count for e in self.entries)


def _checksum(env: Dict[str, str]) -> str:
    """Stable SHA-256 of sorted key=value pairs."""
    blob = "\n".join(f"{k}={v}" for k, v in sorted(env.items()))
    return hashlib.sha256(blob.encode()).hexdigest()[:16]


def build_archive(
    paths: List[Path],
    label: Optional[str] = None,
) -> ArchiveResult:
    """Parse each env file and collect metadata into an ArchiveResult."""
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    result = ArchiveResult(label=label or ts, created_at=ts)
    for p in paths:
        env = parse_env_file(p)
        entry = ArchiveEntry(
            path=str(p),
            key_count=len(env),
            checksum=_checksum(env),
            keys=sorted(env.keys()),
        )
        result.entries.append(entry)
    return result


def save_archive(result: ArchiveResult, dest: Path) -> None:
    """Persist an ArchiveResult as JSON to *dest*."""
    dest.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "label": result.label,
        "created_at": result.created_at,
        "entries": [
            {
                "path": e.path,
                "key_count": e.key_count,
                "checksum": e.checksum,
                "keys": e.keys,
            }
            for e in result.entries
        ],
    }
    dest.write_text(json.dumps(payload, indent=2))


def load_archive(src: Path) -> ArchiveResult:
    """Load an ArchiveResult previously saved with *save_archive*."""
    data = json.loads(src.read_text())
    entries = [
        ArchiveEntry(
            path=e["path"],
            key_count=e["key_count"],
            checksum=e["checksum"],
            keys=e["keys"],
        )
        for e in data["entries"]
    ]
    return ArchiveResult(
        label=data["label"],
        created_at=data["created_at"],
        entries=entries,
    )
