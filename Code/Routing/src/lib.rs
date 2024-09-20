use ordered_float::NotNan;
use petgraph::{
    stable_graph::NodeIndex,
    visit::{EdgeRef, VisitMap, Visitable},
    Directed,
};
use pyo3::{prelude::*, pyclass::CompareOp};
use std::{
    cmp::Reverse,
    collections::{
        hash_map::Entry::{Occupied, Vacant},
        BinaryHeap, HashMap,
    },
};

type EdgeId = usize;
type NodeId = usize;

/// Data associated with the edges of the graph
#[pyclass]
#[derive(Debug, Clone, Default)]
struct Edge {
    #[pyo3(get, set)]
    cost: f32,
    #[pyo3(get, set)]
    max_flow: f32,
}
#[pymethods]
impl Edge {
    #[new]
    fn __new__(cost: f32, max_flow: f32) -> Self {
        Edge { cost, max_flow }
    }
    fn __repr__(&self) -> String {
        format!("{:#?}", self)
    }
}

/// Path through the graph with a cost and flow
#[pyclass]
#[derive(Debug, Clone, Default, PartialEq, PartialOrd)]
struct FlowPath {
    #[pyo3(get, set)]
    cost: f32,
    #[pyo3(get, set)]
    flow: f32,
    #[pyo3(get, set)]
    edges: Vec<EdgeId>,
}
#[pymethods]
impl FlowPath {
    #[new]
    fn __new__(cost: f32, flow: f32, edges: Vec<EdgeId>) -> Self {
        Self { cost, flow, edges }
    }
    fn __repr__(&self) -> String {
        format!("{:#?}", self)
    }
    fn __richcmp__(&self, other: &Self, op: CompareOp) -> bool {
        match self.partial_cmp(&other) {
            Some(ordering) => op.matches(ordering),
            None => false,
        }
    }
}

/// Python wrapper of Rust Graph type.
#[pyclass]
#[derive(Debug, Clone, Default)]
struct Graph(pub petgraph::stable_graph::StableGraph<PyObject, Edge, Directed, usize>);

/// Marker for nodes explored during bfs.
/// Order is reversed for use in a BinaryHeap to make a min-heap and sorted only according to cost.
struct ExploredVal<T> {
    cost: NotNan<f32>,
    inner: T,
}
impl<T> PartialEq for ExploredVal<T> {
    fn eq(&self, other: &Self) -> bool {
        self.cost == other.cost
    }
}
impl<T> Eq for ExploredVal<T> {}
impl<T> PartialOrd for ExploredVal<T> {
    fn partial_cmp(&self, other: &Self) -> Option<std::cmp::Ordering> {
        Reverse(self.cost).partial_cmp(&Reverse(other.cost))
    }
}
impl<T> Ord for ExploredVal<T> {
    fn cmp(&self, other: &Self) -> std::cmp::Ordering {
        self.partial_cmp(other).unwrap()
    }
}

#[pymethods]
impl Graph {
    #[new]
    fn __new__() -> Self {
        Self::default()
    }
    fn __repr__(&self) -> String {
        format!("{:#?}", self.0)
    }
    /// Add node to graph and return its id.
    fn add_node(&mut self, val: PyObject) -> NodeId {
        self.0.add_node(val).index()
    }
    /// Get node with the given node id
    fn get_node(&self, id: NodeId) -> Option<PyObject> {
        // Clone shared pointer `Py<...>`
        self.0.node_weight(id.into()).cloned()
    }
    /// Remove node from graph, if it exists, and return its weight.
    fn remove_node(&mut self, a: NodeId) -> Option<PyObject> {
        self.0.remove_node(a.into())
    }
    /// Get `Nodeid`s in the `Graph`
    fn node_indices(&self) -> Vec<NodeId> {
        self.0.node_indices().map(|x| x.index()).collect()
    }
    /// Node weights in the `Graph`
    fn node_weights(&self) -> Vec<PyObject> {
        // Clone shared pointer `Py<...>`
        self.0.node_weights().cloned().collect()
    }
    /// Add edge from `a` to `b` to graph with associated data `weight` and return its id.
    fn add_edge(&mut self, a: NodeId, b: NodeId, weight: Edge) -> EdgeId {
        self.0.add_edge(a.into(), b.into(), weight).index()
    }
    /// Remove edge from graph. Return the removed edge's data.
    fn remove_edge(&mut self, a: EdgeId) -> Option<Edge> {
        self.0.remove_edge(a.into())
    }
    /// Edge ids in the `Graph`
    fn edge_indices(&self) -> Vec<EdgeId> {
        self.0.edge_indices().map(|x| x.index()).collect()
    }
    /// `(Start, End)` nodes of the given edge
    fn edge_endpoints(&self, id: EdgeId) -> Option<(NodeId, NodeId)> {
        self.0
            .edge_endpoints(id.into())
            .map(|(x, y)| (x.index(), y.index()))
    }
    /// All edges of a, in the specified direction.
    ///
    /// - Outgoing=true: All edges from a.
    /// - Outgoing=false: All edges to a.
    fn edges_directed(&self, a: NodeId, outgoing: bool) -> Vec<EdgeId> {
        let dir = if outgoing {
            petgraph::Direction::Outgoing
        } else {
            petgraph::Direction::Incoming
        };
        self.0
            .edges_directed(a.into(), dir)
            .map(|x| x.id().index())
            .collect()
    }
    /// Finds multiple `FlowPath`s going from `source` to `goal` sorted from lowest cost to highest cost.
    /// The combination of these paths is a minimum cost maximum flow from `source` to `goal`
    fn ranked_max_flow(&self, source: NodeId, goal: NodeId) -> Vec<FlowPath> {
        ranked_max_flow(self.0.clone(), source.into(), goal.into())
    }
    /// Save graph with DOT file syntax. This file can be viewed with a GRAPHVIZ editor.
    fn save_dot(&self, path: std::path::PathBuf) -> PyResult<()> {
        use std::io::Write;
        let mut f = std::fs::File::create(path)?;
        write!(
            f,
            "{:#?}",
            petgraph::dot::Dot::with_config(&self.0, &[petgraph::dot::Config::NodeIndexLabel])
        )?;
        Ok(())
    }
}

/// Finds multiple `FlowPath`s going from `source` to `goal` sorted from lowest cost to highest cost.
/// The combination of these paths is a minimum cost maximum flow from `source` to `goal`
// This is the recursive rust impl that is forwarded to by the python method.
fn ranked_max_flow<N>(
    mut graph: petgraph::stable_graph::StableGraph<N, Edge, Directed, usize>,
    source: NodeIndex<NodeId>,
    goal: NodeIndex<NodeId>,
) -> Vec<FlowPath> {
    // If source and goal are same, shortcut whole algorithm to only edges connecting the source to itself.
    if source == goal {
        return graph
            .edges_connecting(source, source)
            .map(|edge| FlowPath {
                cost: edge.weight().cost,
                flow: edge.weight().max_flow,
                edges: vec![edge.id().index()],
            })
            .collect();
    }

    // Mostly a bfs.
    // Difference is that once the destination is found, the edge with the lowest min_flow on the path is subtracted from the path all edges on the path...
    // ... then repeat searching until the destination can't be reached.

    let mut result = Vec::new();
    let mut visited = graph.visit_map();

    // map from nodes to their cost to reach and the edge used to reach.
    let mut explored = HashMap::new();
    // no edge to reach self and no cost
    explored.insert(
        source,
        ExploredVal {
            cost: NotNan::new(0.).unwrap(),
            inner: None,
        },
    );

    // nodes to explore next with the cost so far to reach them
    let mut visit_next = BinaryHeap::new();
    visit_next.push(ExploredVal {
        cost: NotNan::new(0.).unwrap(),
        inner: source,
    });

    while let Some(current) = visit_next.pop() {
        if visited.is_visited(&current.inner) {
            continue;
        }
        if goal == current.inner {
            // reconstruct the path of edges used to reach the goal
            let mut edge_path = std::iter::successors(explored[&current.inner].inner, |id| {
                explored[&graph.edge_endpoints(*id).unwrap().0].inner
            })
            .collect::<Vec<_>>();
            // sort from beginning to end instead of end to beginning
            edge_path.reverse();
            // find lowest max_flow along the path
            let min = edge_path
                .iter()
                .map(|&id| graph.edge_weight(id).unwrap().max_flow)
                .min_by(|&x, &y| x.total_cmp(&y))
                .expect("nonempty");
            // subtract the lowest max_flow from all edges in the path
            for &id in &edge_path {
                graph.edge_weight_mut(id).unwrap().max_flow -= min;
            }
            // record the path with the max_flow
            result.push(FlowPath {
                flow: min,
                cost: edge_path
                    .iter()
                    .map(|&id| graph.edge_weight(id).unwrap().cost)
                    .sum(),
                edges: edge_path.iter().map(|x| x.index()).collect(),
            });
            // and remove any edges with no max flow left
            for id in edge_path {
                if graph.edge_weight(id).unwrap().max_flow <= 0. {
                    graph.remove_edge(id);
                }
            }
            // recurse the graph with less flow available to the edges
            // the edge with the lowest flow will definitely be removed
            result.extend(ranked_max_flow(graph, source, goal));
            break;
        }
        for edge in graph.edges(current.inner.into()) {
            let next_id = edge.target();
            if visited.is_visited(&next_id) {
                continue;
            }
            let next_score = current.cost + edge.weight().cost;
            match explored.entry(next_id) {
                Occupied(ent) => {
                    if next_score < ent.get().cost {
                        let ent = ent.into_mut();
                        ent.cost = next_score;
                        ent.inner = Some(edge.id());
                        visit_next.push(ExploredVal {
                            cost: next_score,
                            inner: current.inner,
                        });
                    }
                }
                Vacant(ent) => {
                    ent.insert(ExploredVal {
                        cost: next_score,
                        inner: Some(edge.id()),
                    });
                    visit_next.push(ExploredVal {
                        cost: next_score,
                        inner: next_id,
                    });
                }
            }
        }
        visited.visit(current.inner);
    }

    result
}

/// A Python module for routing calculations implemented in Rust.
#[pymodule]
fn routing(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<Edge>()?;
    m.add_class::<FlowPath>()?;
    m.add_class::<Graph>()?;
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_1() {
        let mut graph = petgraph::stable_graph::StableGraph::<(), Edge, Directed, usize>::default();
        let n1 = graph.add_node(());
        let n2 = graph.add_node(());
        let n3 = graph.add_node(());
        let _ = graph.add_edge(
            n2,
            n1,
            Edge {
                cost: 0.,
                max_flow: 1000.,
            },
        );
        let e1 = graph
            .add_edge(
                n1,
                n2,
                Edge {
                    cost: 1.,
                    max_flow: 1.,
                },
            )
            .index();
        let e2 = graph
            .add_edge(
                n1,
                n2,
                Edge {
                    cost: 1.,
                    max_flow: 1.,
                },
            )
            .index();
        assert_eq!(
            ranked_max_flow(graph.clone(), n1, n2),
            vec![
                FlowPath {
                    flow: 1.,
                    cost: 1.,
                    edges: vec![e2]
                },
                FlowPath {
                    flow: 1.,
                    cost: 1.,
                    edges: vec![e1],
                }
            ]
        );
        let e3 = graph
            .add_edge(
                n2,
                n3,
                Edge {
                    cost: 2.,
                    max_flow: 0.5,
                },
            )
            .index();
        assert_eq!(
            ranked_max_flow(graph.clone(), n1, n3),
            vec![FlowPath {
                flow: 0.5,
                cost: 3.,
                edges: vec![e2, e3]
            }]
        );
        let e4 = graph
            .add_edge(
                n1,
                n3,
                Edge {
                    cost: 10.,
                    max_flow: 10.,
                },
            )
            .index();
        assert_eq!(
            ranked_max_flow(graph, n1, n3),
            vec![
                FlowPath {
                    flow: 0.5,
                    cost: 3.,
                    edges: vec![e2, e3]
                },
                FlowPath {
                    flow: 10.,
                    cost: 10.,
                    edges: vec![e4]
                }
            ]
        );
    }
}
