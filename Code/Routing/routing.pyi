from __future__ import annotations
from typing import Any, Optional

type NodeId = int
type EdgeId = int

class Edge:
    """Data associated with the edges of the graph"""

    cost: float
    max_flow: float
    def __new__(cls, cost: float, max_flow: float) -> Edge: ...
    def __repr__(self) -> str: ...

class FlowPath:
    """Path through the graph with a cost and flow"""

    cost: float
    flow: float
    edges: list[EdgeId]
    def __new__(cls, cost: float, flow: float, edges: list[EdgeId]) -> FlowPath: ...
    def __repr__(self) -> str: ...

class Graph:
    """
    Python wrapper of Rust Graph type.
    """
    def __new__(cls) -> Graph: ...
    def __repr__(self) -> str: ...
    def add_node(self, weight: Any) -> NodeId:
        """Add node to graph and return its id."""
    def get_node(self, id: NodeId) -> Optional[Any]:
        """Get node with the given node id"""
    def remove_node(self, a: NodeId) -> Optional[Any]:
        """Remove node from graph, if it exists, and return its weight."""
    def node_indices(self) -> list[NodeId]:
        """Get `Nodeid`s that in the `Graph`"""
    def node_weights(self) -> list[Any]:
        """Node weights in the `Graph`"""
    def add_edge(self, a: NodeId, b: NodeId, weight: Edge) -> EdgeId:
        """Add edge from `a` to `b` to graph with associated data `weight` and return its id."""
    def remove_edge(self, a: EdgeId) -> Optional[Edge]:
        """Remove edge from graph. Return the removed edge's data."""
    def edge_indices(self) -> list[EdgeId]:
        """Edge ids in the `Graph`"""
    def edge_endpoints(self, id: EdgeId) -> Optional[tuple[NodeId, NodeId]]:
        """`(Start, End)` nodes of the given edge"""
    def edges_directed(self, a: NodeId, outgoing: bool) -> list[EdgeId]:
        """
        All edges of a, in the specified direction.

        - Outgoing=true: All edges from a.
        - Outgoing=false: All edges to a.
        """
    def ranked_max_flow(self, source: NodeId, goal: NodeId) -> list[FlowPath]:
        """
        Finds multiple `FlowPath`s going from `source` to `goal` sorted from lowest cost to highest cost.
        The combination of these paths is a minimum cost maximum flow from `source` to `goal`
        """
    def save_dot(self, path: str) -> None:
        """Save graph with DOT file syntax. This file can be viewed with a GRAPHVIZ editor."""
