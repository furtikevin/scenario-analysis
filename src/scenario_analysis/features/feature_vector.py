from scenario_analysis.model.scenario import Scenario
from scenario_analysis.features.basic_stats import BasicStatsExtractor
from scenario_analysis.features.semantic_ai import AISemanticFeatureExtractor


class FeatureVectorBuilder:
    """
    Combines structural and semantic features into a single feature vector.
    """

    def __init__(
        self,
        structural_extractor: BasicStatsExtractor,
        semantic_extractor: AISemanticFeatureExtractor,
    ):
        self.structural_extractor = structural_extractor
        self.semantic_extractor = semantic_extractor

    def build(self, scenario: Scenario) -> dict:
        feature_vector = {}

        # Structural features
        structural_features = self.structural_extractor.extract(scenario)
        feature_vector.update(structural_features)

        # Semantic features (LLM)
        semantic_features = self.semantic_extractor.extract(scenario)
        feature_vector["semantic_analysis"] = semantic_features

        # Metadata
        feature_vector["scenario_name"] = scenario.name

        return feature_vector
