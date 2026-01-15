from pathlib import Path
from lxml import etree
import networkx as nx


class RoadGraphExtractor:
    """
    Extracts a directed graph representation of an OpenDRIVE road network.

    Nodes:
        - road segments (road_id)

    Edges:
        - successor relations between roads
    """

    def extract(self, xodr_path: str | Path) -> nx.DiGraph:
        xodr_path = Path(xodr_path)

        graph = nx.DiGraph()

        tree = etree.parse(str(xodr_path))
        root = tree.getroot()

        # OpenDRIVE typically has no default namespace
        for road in root.findall("road"):
            road_id = road.attrib.get("id")
            if road_id is None:
                continue

            graph.add_node(road_id)

            link = road.find("link")
            if link is not None:
                successor = link.find("successor")
                if successor is not None:
                    target = successor.attrib.get("elementId")
                    if target:
                        graph.add_edge(road_id, target)

        return graph
