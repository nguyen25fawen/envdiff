"""stacker.py – layer multiple .env files into a resolved stack with override tracking."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Tuple
from envdiff.parser import parse_env_file


@dataclass
class StackEntry:
    key: str
    value: str
    source: str  # file path that provided the winning value
    overridden_by: List[Tuple[str, str]] = field(default_factory=list)  # (file, value)


@dataclass
class StackResult:
    entries: Dict[str, StackEntry] = field(default_factory=dict)
    layer_order: List[str] = field(default_factory=list)

    def all_keys(self) -> List[str]:
        return sorted(self.entries.keys())

    def winning_value(self, key: str) -> str:
        return self.entries[key].value

    def was_overridden(self, key: str) -> bool:
        return bool(self.entries[key].overridden_by)


def stack_envs(files: List[str], last_wins: bool = False) -> StackResult:
    """Layer env files; first file wins by default (last_wins reverses priority)."""
    layers = [(f, parse_env_file(f)) for f in files]
    if last_wins:
        layers = list(reversed(layers))

    result = StackResult(layer_order=files)
    seen: Dict[str, Tuple[str, str]] = {}  # key -> (source, value)

    for source, env in layers:
        for key, value in env.items():
            if key not in seen:
                seen[key] = (source, value)
            else:
                # record as override candidate
                entry = result.entries.get(key)
                if entry:
                    entry.overridden_by.append((source, value))

    # Build entries from winners
    for key, (source, value) in seen.items():
        result.entries[key] = StackEntry(key=key, value=value, source=source)

    # Second pass: attach override info
    for source, env in layers:
        for key, value in env.items():
            entry = result.entries.get(key)
            if entry and entry.source != source:
                if (source, value) not in entry.overridden_by:
                    entry.overridden_by.append((source, value))

    return result


def format_stack(result: StackResult, show_overrides: bool = True) -> str:
    lines: List[str] = []
    for key in result.all_keys():
        entry = result.entries[key]
        line = f"{key}={entry.value}  # from {entry.source}"
        lines.append(line)
        if show_overrides and entry.overridden_by:
            for src, val in entry.overridden_by:
                lines.append(f"  # overridden: {key}={val} in {src}")
    return "\n".join(lines)
