"""Dependency graph builder for env key references."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Set
import re

_REF = re.compile(r"\$\{([^}]+)\}|\$([A-Za-z_][A-Za-z0-9_]*)")


@dataclass
class GraphResult:
    edges: Dict[str, List[str]] = field(default_factory=dict)  # key -> keys it depends on
    roots: List[str] = field(default_factory=list)  # keys with no dependencies
    orphans: List[str] = field(default_factory=list)  # referenced but never defined
    cycles: List[List[str]] = field(default_factory=list)


def _refs_in(value: str) -> List[str]:
    return [m[0] or m[1] for m in _REF.findall(value)]


def build_graph(env: Dict[str, str]) -> GraphResult:
    edges: Dict[str, List[str]] = {}
    all_keys: Set[str] = set(env)
    referenced: Set[str] = set()

    for key, value in env.items():
        deps = _refs_in(value)
        edges[key] = deps
        referenced.update(deps)

    roots = [k for k, deps in edges.items() if not deps]
    orphans = sorted(referenced - all_keys)
    cycles = _detect_cycles(edges)

    return GraphResult(edges=edges, roots=sorted(roots), orphans=orphans, cycles=cycles)


def _detect_cycles(edges: Dict[str, List[str]]) -> List[List[str]]:
    visited: Set[str] = set()
    cycles: List[List[str]] = []

    def dfs(node: str, path: List[str], in_stack: Set[str]) -> None:
        if node in in_stack:
            cycle_start = path.index(node)
            cycles.append(path[cycle_start:])
            return
        if node in visited:
            return
        visited.add(node)
        in_stack.add(node)
        for dep in edges.get(node, []):
            dfs(dep, path + [dep], in_stack)
        in_stack.discard(node)

    for key in edges:
        dfs(key, [key], set())

    return cycles


def format_graph(result: GraphResult) -> str:
    lines = []
    lines.append(f"Keys: {len(result.edges)}  Roots: {len(result.roots)}  Orphans: {len(result.orphans)}  Cycles: {len(result.cycles)}")
    if result.orphans:
        lines.append("Undefined references: " + ", ".join(result.orphans))
    if result.cycles:
        for cycle in result.cycles:
            lines.append("Cycle: " + " -> ".join(cycle))
    for key, deps in sorted(result.edges.items()):
        if deps:
            lines.append(f"  {key} <- {', '.join(deps)}")
    return "\n".join(lines)
