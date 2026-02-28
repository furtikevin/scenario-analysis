from scenario_analysis.model.scenario import Scenario
from scenario_analysis.features.basic_stats import BasicStatsExtractor
from scenario_analysis.features.semantic_ai import AISemanticFeatureExtractor
from scenario_analysis.analysis.road_graph import RoadGraphExtractor
from scenario_analysis.features.road_graph_features import RoadGraphFeatureExtractor
from scenario_analysis.analysis.accident_risk import AccidentRiskEstimator


class FeatureVectorBuilder:
    """
    Combines structural, road-network, semantic and risk-related features
    into a single feature vector.
    """

    def __init__(
        self,
        structural_extractor: BasicStatsExtractor,
        semantic_extractor: AISemanticFeatureExtractor,
        road_graph_extractor: RoadGraphExtractor,
        road_graph_feature_extractor: RoadGraphFeatureExtractor,
        xodr_path: str,
    ):
        self.structural_extractor = structural_extractor
        self.semantic_extractor = semantic_extractor
        self.road_graph_extractor = road_graph_extractor
        self.road_graph_feature_extractor = road_graph_feature_extractor
        self.xodr_path = xodr_path
        self.risk_estimator = AccidentRiskEstimator()

    def build(self, scenario: Scenario) -> dict:
        feature_vector = {}

        # Structural features (OpenSCENARIO)
        feature_vector.update(
            self.structural_extractor.extract(scenario)
        )

        # Road network features (OpenDRIVE)
        graph = self.road_graph_extractor.extract(self.xodr_path)
        road_features = self.road_graph_feature_extractor.extract(graph)
        feature_vector.update(road_features)

        # Network risk summary
        hotspots = road_features.get("risk_hotspots", [])
        feature_vector["network_risk_summary"] = {
            "total_hotspots_detected": len(hotspots),
            "high_severity_hotspots": sum(1 for h in hotspots if h.get("severity", 0.0) >= 0.8),
            "types_present": list(set(h.get("type") for h in hotspots))
        }

        # Semantic features (LLM)
        feature_vector["semantic_analysis"] = (
            self.semantic_extractor.extract(scenario)
        )

        # Metadata
        feature_vector["scenario_name"] = scenario.name

        # Accident probability (hybrid)
        feature_vector["accident_probability"] = (
            self.risk_estimator.estimate(feature_vector)
        )

        return feature_vector
