class AccidentRiskEstimator:
    """
    Hybrid accident risk estimator.
    Combines structural, road-based and AI-derived semantic risk.
    """

    def estimate(self, feature_vector: dict) -> float:
        # Structural risk
        num_entities = feature_vector.get("num_entities", 0)
        num_maneuvers = feature_vector.get("num_maneuvers", 0)
        structural_risk = min(1.0, (num_entities + num_maneuvers) / 6)

        # Road topology risk
        num_intersections = feature_vector.get("num_intersections", 0)
        road_risk = min(1.0, num_intersections / 4)

        # AI semantic risk
        semantic = feature_vector.get("semantic_analysis", {})
        ai_risk = semantic.get("riskEstimate", 0.0)

        # Final weighted probability
        final_risk = (
            0.25 * structural_risk +
            0.25 * road_risk +
            0.5 * ai_risk
        )

        return round(final_risk, 3)
