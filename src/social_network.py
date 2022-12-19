import uuid

import networkx as nx

from src.utils import add_random_connections_to_network


class SocialSubNetwork:
    def __init__(
        self,
        number_individuals: int = 30,
        average_connections_per_person: int = 5,
        **kwargs
    ) -> None:
        self.number_individuals = number_individuals
        self.average_connections_per_person = average_connections_per_person
        self.social_network = self.create_network()

    def create_network(self):
        social_network = nx.DiGraph()

        for _ in range(self.number_individuals):
            social_network.add_node(str(uuid.uuid4()))

        max_edges = self.number_individuals**2 - self.number_individuals
        number_edges = min(
            self.number_individuals * self.average_connections_per_person, max_edges
        )

        add_random_connections_to_network(social_network, number_edges)

        social_network.remove_nodes_from(list(nx.isolates(social_network)))

        return social_network

    def get_graph(self):
        return self.social_network
