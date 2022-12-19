import random
import uuid

import networkx as nx
import numpy as np
from tqdm import tqdm

from src.config import Config
from src.local_networks import LocalNetwork
from src.utils import add_random_connections_to_network


class LargeNetwork:
    """
    A large network is the connection of a group of communities. This could be like a county or region
    """

    def __init__(
        self,
        num_local_networks: int = 50,
        num_large_businesses: int = 600,
        num_connections_per_local_network: int = 20,
        **kwargs
    ) -> None:
        """
        Args:
            num_local_networks (int, optional): Number of local networks in a large network. Defaults to 50.
            num_large_businesses (int, optional): Number of large businesses in a large network. Defaults to 600.
            num_connections_per_local_network (int, optional):
                Number of random connections between different local networks to prevent complete separation.
                Defaults to 20.
        """
        self.business_names = set()

        self.large_network = self._link_local_networks(
            num_local_networks, num_connections_per_local_network, **kwargs
        )

        self._add_large_businesses(num_large_businesses)

    def _link_local_networks(
        self, num_social_networks: int, num_connections_per_network: int, **kwargs
    ) -> nx.DiGraph:
        """
        Links a number of local networks into a large network

        Args:
            num_social_networks (int): Number of local networks in a large network.
            num_connections_per_network (int): Number of large businesses in a large network

        Returns:
            nx.DiGraph: Linked networks into a larger network
        """

        # Create starting local network
        local_network = LocalNetwork(**kwargs)
        large_network = local_network.get_graph()
        # keep track of businesses
        self.business_names |= local_network.get_businesses()
        for _ in tqdm(range(num_social_networks - 1)):
            # Create starting local network
            new_local_network = LocalNetwork(**kwargs)
            # keep track of businesses
            self.business_names |= new_local_network.get_businesses()
            # combine
            large_network = nx.union(large_network, new_local_network.get_graph())

        # Add random connections between individuals but not businesses
        large_network = add_random_connections_to_network(
            large_network,
            num_connections_per_network * num_social_networks,
            exclude_nodes=self.business_names,
        )

        return large_network

    def _add_large_businesses(self, num_large_businesses: int):
        """
        Add in businesses that are common to many local networks

        Args:
            num_large_businesses (int): Number of large businesses in a large network
        """

        # get names of all individuals
        customer_nodes = list(set(self.large_network.nodes) - self.business_names)
        num_nodes = len(customer_nodes)

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
                num_large_businesses,
            )
        ]

        for percentage_use_business in percentage_of_users:
            num_users = round(percentage_use_business * num_nodes)
            # sample users from network who shop at the business
            users = random.sample(customer_nodes, k=num_users)
            business_name = str(uuid.uuid4())
            self.business_names.add(business_name)

            self.large_network.add_node(business_name)

            for user in users:
                self.large_network.add_edge(user, business_name)
