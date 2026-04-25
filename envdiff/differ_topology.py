"""Topology analysis: map structural relationships between multiple .env files."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, FrozenSet, List, Set

from envdiff.parser import parse_env_file


@dataclass
class TopologyNode:
    path: str
    keys: FrozenSet[str]

    @property
    def key_count(self) -> int:
        return len(self.keys)


@dataclass
class TopologyEdge:
    source: str
    target: str
    shared_keys: FrozenSet[str]
    overlap_pct: float  # Jaccard similarity * 100


@dataclass
class TopologyResult:
    nodes: List[TopologyNode] = field(default_factory=list)
    edges: List[TopologyEdge] = field(default_factory=list)

    def is_empty(self) -> bool:
        return len(self.nodes) == 0

    def node_for(self, path: str) -> TopologyNode | None:
        return next((n for n in self.nodes if n.path == path), None)

    def edges_for(self, path: str) -> List[TopologyEdge]:
        return [e for e in self.edges if e.source == path or e.target == path]


def _jaccard(a: FrozenSet[str], b: FrozenSet[str]) -> float:
    if not a and not b:
        return 1.0
    union = a | b
    if not union:
        return 0.0
    return len(a & b) / len(union)


def build_topology(paths: List[str]) -> TopologyResult:
    """Build a topology graph from a list of .env file paths."""
    nodes: List[TopologyNode] = []
    for path in paths:
        env = parse_env_file(path)
        nodes.append(TopologyNode(path=path, keys=frozenset(env.keys())))

    edges: List[TopologyEdge] = []
    for i, a in enumerate(nodes):
        for b in nodes[i + 1 :]:
            sim = _jaccard(a.keys, b.keys)
            edges.append(
                TopologyEdge(
                    source=a.path,
                    target=b.path,
                    shared_keys=a.keys & b.keys,
                    overlap_pct=round(sim * 100, 1),
                )
            )

    return TopologyResult(nodes=nodes, edges=edges)
