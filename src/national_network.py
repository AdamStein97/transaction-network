import random
import uuid

import networkx as nx
import numpy as np
from tqdm import tqdm

from src.config import Config
from src.local_networks import LocalNetwork
from src.utils import add_random_connections_to_network


class NationalNetwork:
    def __init__(
        self,
        num_local_networks: int = 50,
        num_national_businesses: int = 600,
        num_connections_per_local_network: int = 20,
        **kwargs
    ) -> None:
        self.business_names = set()

        self.national_network = self._link_local_networks(
            num_local_networks, num_connections_per_local_network, **kwargs
        )

        self._add_national_businesses(num_national_businesses)

    def _link_local_networks(
        self, num_social_networks, num_connections_per_network, **kwargs
    ):
        local_network = LocalNetwork(**kwargs)
        national_network = local_network.get_graph()
        self.business_names |= local_network.get_businesses()
        for _ in tqdm(range(num_social_networks - 1)):
            new_local_network = LocalNetwork(**kwargs)
            self.business_names |= new_local_network.get_businesses()
            national_network = nx.union(national_network, new_local_network.get_graph())

        national_network = add_random_connections_to_network(
            national_network,
            num_connections_per_network * num_social_networks,
            exclude_nodes=self.business_names,
        )

        return national_network

    def _add_national_businesses(self, num_national_businesses):
        customer_nodes = list(set(self.national_network.nodes) - self.business_names)
        num_nodes = len(customer_nodes)

        percentage_of_users = [
            np.clip(
                sample,
                Config.MIN_PERCENTAGE_USE_RETAILER,
                Config.MAX_PERCENTAGE_USE_RETAILER,
            )
            for sample in np.random.normal(
                Config.MEAN_PERCENTAGE_USE_RETAILER,
                Config.VAR_PERCENTAGE_USE_RETAILER,
                num_national_businesses,
            )
        ]

        for percentage_use_business in percentage_of_users:
            num_users = round(percentage_use_business * num_nodes)
            users = random.sample(customer_nodes, k=num_users)
            business_name = str(uuid.uuid4())
            self.business_names.add(business_name)

            self.national_network.add_node(business_name)

            for user in users:
                self.national_network.add_edge(user, business_name)
