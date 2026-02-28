class AccidentRiskEstimator:
    """
    Hybrid accident risk estimator.
    Combines structural, road-based and AI-derived semantic risk.
    """

    def estimate(self, feature_vector: dict) -> float:
        # We need normalizations. We use reasonable maximums to normalize to [0,1].
        # These can be adjusted based on experience.
        max_entities = 10.0
        max_nodes = 50.0  # num_roads as proxy for N
        max_junctions = 10.0 # num_intersections as proxy for J
        max_triggers = 15.0 # num_triggers as proxy for T
        max_conflicts = 5.0 # Max node degree or intersections as proxy for C

        Enorm = min(1.0, feature_vector.get("num_entities", 0) / max_entities)
        Nnorm = min(1.0, feature_vector.get("num_roads", 0) / max_nodes)
        Jnorm = min(1.0, feature_vector.get("num_intersections", 0) / max_junctions)
        Tnorm = min(1.0, feature_vector.get("num_triggers", 0) / max_triggers)
        
        # We use the aggregated total severity of all detected risk_hotspots for Cnorm
        # instead of a rough proxy like max_node_degree + num_intersections.
        risk_hotspots = feature_vector.get("risk_hotspots", [])
        total_hotspot_severity = sum(spot.get("severity", 0.0) for spot in risk_hotspots)
        Cnorm = min(1.0, total_hotspot_severity / max_conflicts)
        
        # Kinematics Factor (Vnorm)
        # Assume 36 m/s (~130 km/h) as max reasonable speed for scaling
        max_speed = 36.0 
        Vnorm = min(1.0, feature_vector.get("max_speed_ms", 0.0) / max_speed)

        # Adjusted struct formula including kinematics
        Rstruct = (
            0.20 * Enorm +
            0.20 * Nnorm +
            0.15 * Jnorm +
            0.15 * Tnorm +
            0.15 * Cnorm +
            0.15 * Vnorm
        )
        
        # AI semantic risk
        semantic = feature_vector.get("semantic_analysis", {})
        raw_risk = semantic.get("riskEstimate", 0.0)
        
        try:
            rllm_val = float(raw_risk)
        except (ValueError, TypeError):
            # Fallback mapping if LLM returns a string despite instructions
            raw_str = str(raw_risk).lower()
            if any(word in raw_str for word in ["severe", "critical", "extreme"]):
                rllm_val = 0.9
            elif any(word in raw_str for word in ["high", "elevated", "significant"]):
                rllm_val = 0.8
            elif any(word in raw_str for word in ["medium", "moderate"]):
                rllm_val = 0.5
            elif any(word in raw_str for word in ["low", "minimal", "safe"]):
                rllm_val = 0.2
            else:
                rllm_val = 0.5
                
        # Ensure RLLM is between 0 and 1
        RLLM = min(1.0, max(0.0, rllm_val))

        # Final weighted probability according to thesis
        Rfinal = 0.3 * Rstruct + 0.7 * RLLM

        return round(Rfinal, 3)
