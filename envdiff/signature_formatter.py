"""Format SignatureResult for terminal output."""
from __future__ import annotations

from typing import List

from envdiff.differ_signature import SignatureResult, unique_structures, structurally_equivalent


def _c(text: str, code: str) -> str:
    return f"\033[{code}m{text}\033[0m"


def format_signature_rich(
    result: SignatureResult,
    *,
    show_keys: bool = False,
) -> str:
    lines: List[str] = []
    lines.append(_c("Structural Signatures", "1;36"))
    lines.append("")

    for entry in result.entries:
        sig_label = _c(entry.signature, "33")
        lines.append(f"  {entry.path}")
        lines.append(f"    signature : {sig_label}")
        lines.append(f"    key count : {len(entry.keys)}")
        if show_keys:
            for k in entry.keys:
                lines.append(f"      - {k}")
        lines.append("")

    n = unique_structures(result)
    if structurally_equivalent(result):
        status = _c("all files share the same structure", "32")
    else:
        status = _c(f"{n} distinct structures detected", "31")

    lines.append(f"  {status}")

    if not structurally_equivalent(result):
        lines.append("")
        lines.append(_c("  Groups:", "1"))
        for sig, paths in result.groups.items():
            lines.append(f"    [{_c(sig, '33')}]")
            for p in paths:
                lines.append(f"      {p}")

    return "\n".join(lines)


def format_signature_summary(result: SignatureResult) -> str:
    n = len(result.entries)
    u = unique_structures(result)
    equiv = structurally_equivalent(result)
    status = "equivalent" if equiv else "divergent"
    return f"Checked {n} file(s): {u} unique structure(s) — {status}"
