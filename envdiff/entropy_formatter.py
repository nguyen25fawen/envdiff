"""Formatters for EntropyResult."""
from __future__ import annotations

from envdiff.differ_entropy import EntropyEntry, EntropyResult

_RESET = "\033[0m"
_BOLD = "\033[1m"


def _c(text: str, code: str) -> str:
    return f"{code}{text}{_RESET}"


def _entropy_color(entry: EntropyEntry) -> str:
    if entry.is_uniform:
        return "\033[32m"   # green
    if entry.is_chaotic:
        return "\033[31m"   # red
    return "\033[33m"        # yellow


def _bar(entropy: float, width: int = 10) -> str:
    filled = min(int(entropy * width), width)
    return "[" + "#" * filled + "-" * (width - filled) + "]"


def format_entropy_rich(result: EntropyResult) -> str:
    if result.is_empty():
        return "No keys found."

    lines = [
        _c(f"Entropy report ({result.total_files} files)", _BOLD),
        "",
    ]
    for entry in result.entries:
        color = _entropy_color(entry)
        bar = _bar(entry.entropy)
        label = "uniform" if entry.is_uniform else ("chaotic" if entry.is_chaotic else "mixed")
        lines.append(
            f"  {_c(entry.key, color):<40} "
            f"{_c(bar, color)} "
            f"H={entry.entropy:.3f}  unique={entry.unique_count}/{entry.total_count}  [{label}]"
        )

    chaotic = result.chaotic_keys()
    if chaotic:
        lines += ["", _c(f"  {len(chaotic)} high-entropy key(s) detected.", "\033[31m")]

    return "\n".join(lines)


def format_entropy_summary(result: EntropyResult) -> str:
    total = len(result.entries)
    uniform = len(result.uniform_keys())
    chaotic = len(result.chaotic_keys())
    mixed = total - uniform - chaotic
    return (
        f"Entropy: {total} keys | "
        f"{uniform} uniform | "
        f"{mixed} mixed | "
        f"{chaotic} chaotic"
    )
