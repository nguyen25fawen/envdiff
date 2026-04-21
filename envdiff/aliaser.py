"""aliaser.py – map legacy key names to their canonical replacements."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Tuple


@dataclass
class AliasRule:
    old: str
    new: str


@dataclass
class AliasResult:
    renamed: List[Tuple[str, str]] = field(default_factory=list)   # (old, new)
    already_present: List[str] = field(default_factory=list)        # new key existed
    unknown: List[str] = field(default_factory=list)                # old key not found


def any_renamed(result: AliasResult) -> bool:
    return bool(result.renamed)


def load_alias_rules(path: str | Path) -> List[AliasRule]:
    """Parse a file where each non-comment line is  old=new."""
    rules: List[AliasRule] = []
    for raw in Path(path).read_text().splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        old, _, new = line.partition("=")
        old, new = old.strip(), new.strip()
        if old and new:
            rules.append(AliasRule(old=old, new=new))
    return rules


def apply_aliases(
    env: Dict[str, str],
    rules: List[AliasRule],
    *,
    overwrite: bool = False,
) -> Tuple[Dict[str, str], AliasResult]:
    """Return a new env dict with aliases applied and an AliasResult summary."""
    result = AliasResult()
    out = dict(env)
    for rule in rules:
        if rule.old not in env:
            result.unknown.append(rule.old)
            continue
        if rule.new in out and not overwrite:
            result.already_present.append(rule.new)
            continue
        out[rule.new] = out.pop(rule.old)
        result.renamed.append((rule.old, rule.new))
    return out, result
