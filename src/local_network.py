import random
import uuid
from typing import Set

import networkx as nx
import numpy as np

from src.config import Config
from src.social_network import SocialSubNetwork
from src.utils import add_random_connections_to_network


class LocalNetwork:
    """
    A local network is like a local community. Connections are far more sparse between
    individuals in separate social networks but they are linked by businesses
    """

    def __init__(
        self,
        num_social_networks: int = 50,
        num_local_businesses: int = 200,
        num_connections_per_social_network: int = 5,
        **kwargs
    ):
        """
        Args:
            num_social_networks (int, optional): Number of social networks in a local network. Defaults to 50.
            num_local_businesses (int, optional): Number of businesses in a local network. Defaults to 200.
            num_connections_per_social_network (int, optional):
                Number of random connections between different social networks to prevent complete separation.
                Defaults to 5.
        """

        self._local_network = self._link_social_networks(
            num_social_networks, num_connections_per_social_network, **kwargs
        )

        self._local_business_names = self._add_local_businesses(num_local_businesses)

    def _link_social_networks(
        self, num_social_networks: int, num_connections_per_network: int, **kwargs
    ) -> nx.DiGraph:
        # creates starting network
        local_network = SocialSubNetwork(**kwargs).get_graph()
        for _ in range(num_social_networks - 1):
            # create a new network and combine the graphs
            local_network = nx.union(
                local_network, SocialSubNetwork(**kwargs).get_graph()
            )

        # add some random connections to prevent complete separation
        local_network = add_random_connections_to_network(
            local_network, num_connections_per_network * num_social_networks
        )

        return local_network

    def _add_local_businesses(self, num_local_businesses: int) -> Set[str]:
        """
        Add in businesses that are common to many networks

        Args:
            num_local_businesses (int): Number of businesses in a local network

        Returns:
            Set[str]: Set of business names
        """

        # get names of all individuals
        graph_nodes = list(self._local_network.nodes)
        num_nodes = len(graph_nodes)
        local_business_names = set()

        # sample from a normal distribution to decide business popularity
        percentage_of_users = [
            # Clip values so they can no be too small or too large
            np.clip(
                sample,
                Config.MIN_PERCENTAGE_USE_RETAILER,
                Config.MAX_PERCENTAGE_USE_RETAILER,
            )
            for sample in np.random.normal(
                Config.MEAN_PERCENTAGE_USE_RETAILER,
                Config.VAR_PERCENTAGE_USE_RETAILER,
                num_local_businesses,
            )
        ]

        for percentage_use_business in percentage_of_users:
            num_users = round(percentage_use_business * num_nodes)
            # sample users from network who shop at the business
            users = random.sample(graph_nodes, k=num_users)

            # keep track of business names because they behave differently
            business_name = str(uuid.uuid4())
            local_business_names.add(business_name)

            # Add in node
            self._local_network.add_node(business_name)

            # Add in edges
            for user in users:
                self._local_network.add_edge(user, business_name)

        return local_business_names

    def get_graph(self) -> nx.DiGraph:
        """
        Gets the networkx graph
        """
        return self._local_network

    def get_businesses(self) -> Set[str]:
        """
        Gets the names of all the local businesses
        """
        return self._local_business_names
