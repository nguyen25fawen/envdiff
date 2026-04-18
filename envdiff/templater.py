"""Generate a .env.template file from one or more env files."""
from __future__ import annotations

from pathlib import Path
from typing import Iterable

from envdiff.parser import parse_env_file


def build_template(
    paths: Iterable[str | Path],
    placeholder: str = "",
    comment: bool = True,
) -> dict[str, str]:
    """Return an ordered dict of all keys found across *paths* with empty values."""
    template: dict[str, str] = {}
    sources: dict[str, str] = {}  # key -> first file that defined it

    for path in paths:
        p = Path(path)
        env = parse_env_file(p)
        for key in env:
            if key not in template:
                template[key] = placeholder
                sources[key] = p.name

    return template, sources


def render_template(
    template: dict[str, str],
    sources: dict[str, str],
    include_source_comments: bool = True,
) -> str:
    """Render the template dict as .env file text."""
    lines: list[str] = []
    for key, value in template.items():
        if include_source_comments and key in sources:
            lines.append(f"# source: {sources[key]}")
        lines.append(f"{key}={value}")
    return "\n".join(lines) + "\n"


def write_template(
    paths: Iterable[str | Path],
    output: str | Path,
    placeholder: str = "",
    include_source_comments: bool = True,
) -> Path:
    """Build and write a template file; return the output Path."""
    template, sources = build_template(paths, placeholder=placeholder)
    text = render_template(template, sources, include_source_comments=include_source_comments)
    out = Path(output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text)
    return out
