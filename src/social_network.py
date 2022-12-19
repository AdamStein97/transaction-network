import uuid

import networkx as nx

from src.utils import add_random_connections_to_network


class SocialSubNetwork:
    """
    A small but highly connected social network, imagine this to be like an extended group of friends
    """

    def __init__(
        self,
        number_individuals: int = 30,
        average_connections_per_person: int = 5,
        **kwargs
    ) -> None:
        """
        Args:
            number_individuals (int, optional): number of individuals in the group. Defaults to 30.
            average_connections_per_person (int, optional): average number of payment connections each person has within the group. Defaults to 5.
        """
        self._social_network = self.create_network(
            number_individuals, average_connections_per_person
        )

    def create_network(
        self, number_individuals: int, average_connections_per_person: int
    ) -> nx.DiGraph:
        """
        Creates a directed network graph of the social payment network

        Returns:
            nx.DiGraph: networkx graph
        """
        # create empty graph
        social_network = nx.DiGraph()

        # create a set of nodes
        for _ in range(number_individuals):
            # uuid string used for fake data
            # in practice this would be some unique identifier e.g. account number + sort code
            social_network.add_node(str(uuid.uuid4()))

        number_edges = number_individuals * average_connections_per_person

        # Add in random connections within the group
        add_random_connections_to_network(social_network, number_edges)

        # Remove any isolated nodes after the random procedure
        social_network.remove_nodes_from(list(nx.isolates(social_network)))

        return social_network

    def get_graph(self) -> nx.DiGraph:
        """
        Gets the networkx graph
        """
        return self._social_network
