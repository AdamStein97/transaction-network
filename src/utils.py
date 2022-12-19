import random
from typing import Set


def add_random_connections_to_network(
    nx_graph, number_edges_to_add: int, exclude_nodes: Set[str] = None
):
    if exclude_nodes is None:
        exclude_nodes = set()

    node_names = list(set(nx_graph.nodes) - exclude_nodes)
    num_nodes = len(node_names)

    for _ in range(number_edges_to_add):
        edge = [random.randint(0, num_nodes - 1), random.randint(0, num_nodes - 1)]
        if edge[0] != edge[1]:
            nx_graph.add_edge(node_names[edge[0]], node_names[edge[1]])
            nx_graph.add_edge(node_names[edge[1]], node_names[edge[0]])

    return nx_graph
