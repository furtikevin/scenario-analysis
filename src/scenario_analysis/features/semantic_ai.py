from scenario_analysis.model.scenario import Scenario
from scenario_analysis.llm.openai_client import OpenAIClient


class AISemanticFeatureExtractor:
    def __init__(self, llm: OpenAIClient):
        self.llm = llm

    def _build_prompt(self, scenario: Scenario) -> str:
        lines = []

        lines.append(f"Scenario name: {scenario.name}")
        lines.append(f"Number of entities: {len(scenario.entities)}")

        for e in scenario.entities:
            lines.append(f"- Entity: {e.name} ({e.type})")

        for story in scenario.stories:
            lines.append(f"Story: {story.name}")
            for act in story.acts:
                lines.append(f"  Act: {act.name}")
                for man in act.maneuvers:
                    lines.append(f"    Maneuver: {man.name}")
                    for ev in man.events:
                        lines.append(f"      Event: {ev.name}")
                        if ev.trigger:
                            for c in ev.trigger.conditions:
                                lines.append(f"        Condition: {c.type}")

        lines.append(
                        """
            Based on the scenario structure above:

            Please analyze the scenario step-by-step. 
            First, identify the actors. Second, analyze their geometric and kinematic conflicts. 
            Third, deduce the potential severity. Finally, provide the riskEstimate based solely on your reasoning.
            
            Return ONLY valid JSON. Do not include explanations or markdown outside the JSON.
            Return valid JSON with exactly the following keys:
            - reasoning_path (a string containing your step-by-step analysis)
            - scenarioType
            - interactionDescription
            - scenarioComplexity
            - potentialRiskFactors
            - riskEstimate
            - riskLevel
            """
        )

        return "\n".join(lines)

    def extract(self, scenario: Scenario) -> dict:
        prompt = self._build_prompt(scenario)
        try:
            result = self.llm.analyze_scenario(prompt)
            # Remove reasoning path from final output to keep JSON clean for the thesis
            result.pop("reasoning_path", None)
            return result
        except Exception as e:
            import logging
            logging.warning(f"OpenAI API call failed: {e}. Using fallback mock data.")
            # Fallback mock data with reasoning path (which gets popped anyway, or we just don't include it here since it's a fallback)
            return {
                "scenarioType": "Mocked Scenario (API Quota Exceeded)",
                "interactionDescription": "API unavailable to analyze interactions.",
                "scenarioComplexity": 3,
                "potentialRiskFactors": ["Unable to determine due to API error"],
                "riskEstimate": 0.5,
                "riskLevel": "medium"
            }
