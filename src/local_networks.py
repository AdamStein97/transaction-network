import random
import uuid

import networkx as nx
import numpy as np

from src.config import Config
from src.social_network import SocialSubNetwork
from src.utils import add_random_connections_to_network


class LocalNetwork:
    def __init__(
        self,
        num_social_networks=50,
        num_local_businesses=200,
        num_connections_per_local_network: int = 5,
        **kwargs
    ):

        self.local_network = self._link_social_networks(
            num_social_networks, num_connections_per_local_network, **kwargs
        )

        self.local_business_names = self._add_local_businesses(num_local_businesses)

    def _link_social_networks(
        self, num_social_networks, num_connections_per_network, **kwargs
    ):
        local_network = SocialSubNetwork(**kwargs).get_graph()
        for _ in range(num_social_networks - 1):
            local_network = nx.union(
                local_network, SocialSubNetwork(**kwargs).get_graph()
            )

        local_network = add_random_connections_to_network(
            local_network, num_connections_per_network * num_social_networks
        )

        return local_network

    def _add_local_businesses(self, num_local_businesses):
        graph_nodes = list(self.local_network.nodes)
        num_nodes = len(graph_nodes)
        local_business_names = set()

        percentage_of_users = [
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
            users = random.sample(graph_nodes, k=num_users)
            business_name = str(uuid.uuid4())
            local_business_names.add(business_name)

            self.local_network.add_node(business_name)

            for user in users:
                self.local_network.add_edge(user, business_name)

        return local_business_names

    def get_graph(self):
        return self.local_network

    def get_businesses(self):
        return self.local_business_names
