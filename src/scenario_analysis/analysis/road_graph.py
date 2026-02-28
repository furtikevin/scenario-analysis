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
                
            # Count lanes
            num_lanes = 0
            lanes_el = road.find("lanes")
            if lanes_el is not None:
                for lane_sec in lanes_el.findall("laneSection"):
                    # We can just count all <lane> elements except the center lane (id=0),
                    # or count all that have type="driving". Let's count type="driving".
                    for side in ["left", "right"]:
                        side_el = lane_sec.find(side)
                        if side_el is not None:
                            for lane in side_el.findall("lane"):
                                if lane.attrib.get("type", "") == "driving":
                                    num_lanes += 1

            graph.add_node(road_id, num_lanes=num_lanes)

            link = road.find("link")
            if link is not None:
                successor = link.find("successor")
                if successor is not None:
                    target = successor.attrib.get("elementId")
                    if target:
                        graph.add_edge(road_id, target)

        return graph
