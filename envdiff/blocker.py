"""Block deployments by asserting required keys meet conditions."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Dict
from envdiff.parser import parse_env_file


@dataclass
class BlockRule:
    key: str
    reason: str
    must_be_set: bool = True
    forbidden_values: List[str] = field(default_factory=list)


@dataclass
class BlockResult:
    path: str
    violations: List[str] = field(default_factory=list)

    @property
    def is_blocked(self) -> bool:
        return len(self.violations) > 0


def load_block_rules(rules_path: str) -> List[BlockRule]:
    """Load block rules from a simple text file.

    Format per line:  KEY [forbidden=val1,val2] # reason
    Lines starting with # are comments.
    """
    rules: List[BlockRule] = []
    with open(rules_path) as fh:
        for raw in fh:
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            reason = ""
            if "#" in line:
                line, reason = line.split("#", 1)
                reason = reason.strip()
            parts = line.split()
            if not parts:
                continue
            key = parts[0]
            forbidden: List[str] = []
            for part in parts[1:]:
                if part.startswith("forbidden="):
                    forbidden = part[len("forbidden="):].split(",")
            rules.append(BlockRule(key=key, reason=reason, forbidden_values=forbidden))
    return rules


def check_env(path: str, rules: List[BlockRule]) -> BlockResult:
    env: Dict[str, str] = parse_env_file(path)
    result = BlockResult(path=path)
    for rule in rules:
        value = env.get(rule.key)
        if rule.must_be_set and (value is None or value == ""):
            msg = f"{rule.key} is not set"
            if rule.reason:
                msg += f" ({rule.reason})"
            result.violations.append(msg)
        elif value is not None and value in rule.forbidden_values:
            msg = f"{rule.key}={value!r} is a forbidden value"
            if rule.reason:
                msg += f" ({rule.reason})"
            result.violations.append(msg)
    return result
