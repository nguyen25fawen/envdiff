"""Tag keys in an env file with custom labels for grouping and filtering."""
from __future__ import annotations

from dataclasses import dataclass, field
from fnmatch import fnmatch
from pathlib import Path
from typing import Dict, List


@dataclass
class TagResult:
    tags: Dict[str, List[str]] = field(default_factory=dict)  # key -> list of tags

    def keys_for_tag(self, tag: str) -> List[str]:
        return sorted(k for k, tags in self.tags.items() if tag in tags)

    def all_tags(self) -> List[str]:
        seen: set[str] = set()
        for tags in self.tags.values():
            seen.update(tags)
        return sorted(seen)


def load_tag_rules(path: Path) -> Dict[str, List[str]]:
    """Load tag rules from a file.

    Format:  TAG: PATTERN[, PATTERN ...]
    Lines starting with # are comments.
    """
    rules: Dict[str, List[str]] = {}
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" not in line:
            continue
        tag, _, patterns_raw = line.partition(":")
        tag = tag.strip()
        patterns = [p.strip() for p in patterns_raw.split(",") if p.strip()]
        rules.setdefault(tag, []).extend(patterns)
    return rules


def tag_keys(keys: List[str], rules: Dict[str, List[str]]) -> TagResult:
    """Apply tag rules to a list of keys."""
    result = TagResult()
    for key in keys:
        matched: List[str] = []
        for tag, patterns in rules.items():
            if any(fnmatch(key, p) for p in patterns):
                matched.append(tag)
        if matched:
            result.tags[key] = sorted(matched)
    return result


def tag_env(env: Dict[str, str], rules: Dict[str, List[str]]) -> TagResult:
    return tag_keys(list(env.keys()), rules)
