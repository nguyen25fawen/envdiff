"""Format DiffResult into human-readable console output."""

from typing import Optional

from envdiff.comparator import DiffResult

ANSI_RED = "\033[31m"
ANSI_YELLOW = "\033[33m"
ANSI_GREEN = "\033[32m"
ANSI_RESET = "\033[0m"


def _colored(text: str, color: str, use_color: bool) -> str:
    if use_color:
        return f"{color}{text}{ANSI_RESET}"
    return text


def format_diff(
    result: DiffResult,
    first_label: str = "first",
    second_label: str = "second",
    use_color: bool = True,
    mask_values: bool = True,
) -> str:
    """Render a DiffResult as a printable string."""
    lines = []

    if not result.has_differences:
        lines.append(_colored("No differences found.", ANSI_GREEN, use_color))
        return "\n".join(lines)

    if result.missing_in_second:
        lines.append(
            _colored(f"Keys in '{first_label}' but missing in '{second_label}':", ANSI_RED, use_color)
        )
        for key in result.missing_in_second:
            lines.append(f"  - {key}")

    if result.missing_in_first:
        lines.append(
            _colored(f"Keys in '{second_label}' but missing in '{first_label}':", ANSI_RED, use_color)
        )
        for key in result.missing_in_first:
            lines.append(f"  - {key}")

    if result.value_mismatches:
        lines.append(
            _colored("Value mismatches:", ANSI_YELLOW, use_color)
        )
        for key, (val_a, val_b) in result.value_mismatches.items():
            if mask_values:
                display = f"  ~ {key}: <hidden> != <hidden>"
            else:
                display = f"  ~ {key}: {val_a!r} != {val_b!r}"
            lines.append(display)

    return "\n".join(lines)
