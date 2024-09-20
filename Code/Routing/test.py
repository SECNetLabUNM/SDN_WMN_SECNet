from operator import attrgetter
from routing import routing, FlowPath, Graph, Edge  # type: ignore


# force pass by reference
class wrapper:
    def __init__(self) -> None:
        self.x = 0


print(routing.__all__)
print(routing.__doc__)
print(routing.Edge.__doc__)
print(routing.FlowPath.__doc__)
print(routing.Graph.__doc__)
graph = Graph()
n1 = graph.add_node(3)
assert graph.get_node(n1) == 3
n2 = graph.add_node(2)
n3 = graph.add_node(wrapper())
val: wrapper = graph.get_node(n3)  # type: ignore
assert val.x == 0
val.x = 3
assert graph.get_node(n3).x == 3  # type: ignore
n4 = graph.add_node(())
e1 = graph.add_edge(n1, n2, Edge(3, 4))
e2 = graph.add_edge(n2, n3, Edge(123, 123))
e3 = graph.add_edge(n3, n4, Edge(0.1, 10))
e4 = graph.add_edge(n1, n4, Edge(8, 10))
path = FlowPath(3, 4, [e1])
assert graph.ranked_max_flow(n1, n2) == [path]
path.cost = 123 + 0.1
path.flow = min(123, 10.0)
path.edges = [e2, e3]
assert graph.ranked_max_flow(n2, n4) == [path]
paths = [FlowPath(8, 10, [e4]), FlowPath(3 + 123 + 0.1, 4, [e1, e2, e3])]
assert graph.ranked_max_flow(n1, n4) == paths
print(graph.node_indices())
assert graph.node_indices() == [n1, n2, n3, n4]
assert graph.node_weights() == list(
    map(lambda x: graph.get_node(x), graph.node_indices())
)
assert graph.edge_indices() == [e1, e2, e3, e4]
assert graph.edge_endpoints(e3) == (n3, n4)
graph.save_dot("out.dot")
# sort by flow instead of cost
print(sorted(graph.ranked_max_flow(n1, n4), key=attrgetter("flow")))
