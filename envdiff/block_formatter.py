"""Format BlockResult for terminal output."""
from __future__ import annotations
from typing import List
from envdiff.blocker import BlockResult


def _c(text: str, code: str) -> str:
    return f"\033[{code}m{text}\033[0m"


def format_block_result(result: BlockResult, *, color: bool = True) -> str:
    lines: List[str] = []
    label = result.path
    if result.is_blocked:
        header = f"BLOCKED  {label}" if not color else _c("✖ BLOCKED", "31") + f"  {label}"
        lines.append(header)
        for v in result.violations:
            prefix = "  • " if not color else "  " + _c("•", "31") + " "
            lines.append(f"{prefix}{v}")
    else:
        ok = "OK" if not color else _c("✔ OK", "32")
        lines.append(f"{ok}  {label}")
    return "\n".join(lines)


def format_block_summary(results: List[BlockResult], *, color: bool = True) -> str:
    blocked = [r for r in results if r.is_blocked]
    total = len(results)
    n_blocked = len(blocked)
    if n_blocked == 0:
        msg = f"All {total} file(s) passed block checks."
        return msg if not color else _c(msg, "32")
    msg = f"{n_blocked}/{total} file(s) blocked."
    return msg if not color else _c(msg, "31")
