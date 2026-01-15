import networkx as nx
from typing import Dict


class RoadGraphFeatureExtractor:
    """
    Computes numerical features from a road graph.
    """

    def extract(self, graph: nx.DiGraph) -> Dict[str, int]:
        num_roads = graph.number_of_nodes()
        num_connections = graph.number_of_edges()

        # Intersection heuristic:
        # nodes with more than one incoming or outgoing edge
        num_intersections = sum(
            1 for n in graph.nodes
            if graph.in_degree(n) + graph.out_degree(n) > 2
        )

        return {
            "num_roads": num_roads,
            "num_connections": num_connections,
            "num_intersections": num_intersections,
        }
