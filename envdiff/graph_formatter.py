"""Rich formatter for GraphResult."""
from __future__ import annotations
from envdiff.grapher import GraphResult


def _c(text: str, code: str) -> str:
    return f"\033[{code}m{text}\033[0m"


def format_graph_rich(result: GraphResult, *, show_all: bool = False) -> str:
    lines: list[str] = []
    header = _c("Dependency Graph", "1;34")
    lines.append(header)
    lines.append(
        f"  Keys: {len(result.edges)}  "
        f"Roots: {_c(str(len(result.roots)), '32')}  "
        f"Orphans: {_c(str(len(result.orphans)), '33')}  "
        f"Cycles: {_c(str(len(result.cycles)), '31')}"
    )

    if result.orphans:
        lines.append(_c("Undefined references:", "33"))
        for o in result.orphans:
            lines.append(f"  {_c('!', '33')} {o}")

    if result.cycles:
        lines.append(_c("Cycles detected:", "31"))
        for cycle in result.cycles:
            lines.append("  " + _c(" -> ".join(cycle), "31"))

    if show_all or result.edges:
        lines.append("Dependencies:")
        for key, deps in sorted(result.edges.items()):
            if deps or show_all:
                dep_str = ", ".join(deps) if deps else _c("none", "90")
                lines.append(f"  {_c(key, '36')} <- {dep_str}")

    return "\n".join(lines)


def format_graph_summary(result: GraphResult) -> str:
    parts = [
        f"{len(result.edges)} keys",
        f"{len(result.roots)} roots",
        f"{len(result.orphans)} orphans",
        f"{len(result.cycles)} cycles",
    ]
    status = _c("OK", "32") if not result.orphans and not result.cycles else _c("ISSUES", "31")
    return f"Graph [{status}]: " + ", ".join(parts)
