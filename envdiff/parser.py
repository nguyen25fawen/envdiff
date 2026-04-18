"""Parser for .env files."""

import re
from pathlib import Path


ENV_LINE_RE = re.compile(
    r'^\s*(?P<key>[A-Za-z_][A-Za-z0-9_]*)\s*=\s*(?P<value>.*)\s*$'
)


def parse_env_file(path: str | Path) -> dict[str, str]:
    """Parse a .env file and return a dict of key-value pairs.

    - Lines starting with '#' are treated as comments and ignored.
    - Empty lines are ignored.
    - Values may optionally be quoted with single or double quotes.
    """
    env: dict[str, str] = {}
    file_path = Path(path)

    if not file_path.exists():
        raise FileNotFoundError(f"env file not found: {file_path}")

    with file_path.open(encoding="utf-8") as fh:
        for lineno, raw_line in enumerate(fh, start=1):
            line = raw_line.strip()

            if not line or line.startswith("#"):
                continue

            match = ENV_LINE_RE.match(line)
            if not match:
                raise ValueError(
                    f"Invalid syntax at {file_path}:{lineno}: {raw_line.rstrip()!r}"
                )

            key = match.group("key")
            value = _strip_quotes(match.group("value").strip())
            env[key] = value

    return env


def _strip_quotes(value: str) -> str:
    """Remove surrounding single or double quotes from a value."""
    if len(value) >= 2 and value[0] == value[-1] and value[0] in ('"', "'"):
        return value[1:-1]
    return value
