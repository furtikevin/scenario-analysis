import networkx as nx
from typing import Dict, Any


class RoadGraphFeatureExtractor:
    """
    Computes numerical features and detects risk hotspots from a road graph.
    """

    def extract(self, graph: nx.DiGraph) -> Dict[str, Any]:
        num_roads = graph.number_of_nodes()
        num_connections = graph.number_of_edges()

        # Intersection heuristic:
        # nodes with more than one incoming or outgoing edge
        num_intersections = sum(
            1 for n in graph.nodes
            if graph.in_degree(n) + graph.out_degree(n) > 2
        )
        
        max_node_degree = 0
        if num_roads > 0:
            max_node_degree = max(graph.in_degree(n) + graph.out_degree(n) for n in graph.nodes)
            
        num_lanes = 0
        for n in graph.nodes:
            num_lanes += graph.nodes[n].get("num_lanes", 0)

        # Hotspot Detection 
        risk_hotspots = []
        for n in graph.nodes:
            in_deg = graph.in_degree(n)
            out_deg = graph.out_degree(n)
            total_deg = in_deg + out_deg
            
            node_lanes = graph.nodes[n].get("num_lanes", 0)
            
            # Rule 1: Complex Intersection (Very high degree)
            if total_deg >= 4:
                risk_hotspots.append({
                    "road_id": n,
                    "type": "Complex Intersection",
                    "severity": min(1.0, total_deg / 8.0),
                    "description": f"Highly connected junction with {total_deg} connections."
                })
            # Rule 2: Merge / Bottleneck (Multiple roads flowing into one, or lane reduction)
            # In a directed graph, if in_deg > out_deg and out_deg > 0
            elif in_deg > out_deg and out_deg > 0:
                risk_hotspots.append({
                    "road_id": n,
                    "type": "Merge / Bottleneck",
                    "severity": 0.7,
                    "description": f"Bottleneck detected. {in_deg} incoming links merge into {out_deg} outgoing."
                })
            # Rule 3: High-capacity junction
            elif node_lanes >= 4 and total_deg >= 3:
                 risk_hotspots.append({
                    "road_id": n,
                    "type": "Multi-lane Junction",
                    "severity": 0.8,
                    "description": f"Large multi-lane structure ({node_lanes} lanes) intersecting."
                })

        return {
            "num_roads": num_roads,
            "num_connections": num_connections,
            "num_intersections": num_intersections,
            "max_node_degree": max_node_degree,
            "num_lanes": num_lanes,
            "risk_hotspots": risk_hotspots
        }
