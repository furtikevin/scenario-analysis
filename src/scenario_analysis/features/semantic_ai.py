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

            1. Classify the scenario type.
            2. Describe the interaction between the ego vehicle and other actors.
            3. Rate the scenario complexity on a scale from 1 (simple) to 5 (very complex).
            4. Identify potential risk factors.
            5. Estimate the probability of an accident occurring in this scenario on a scale from 0.0 to 1.0, assuming no external intervention and realistic driver behavior.
            6. Classify the accident risk as one of: low, medium, high.

            Return ONLY valid JSON. Do not include explanations or markdown.
            Return valid JSON with exactly the following keys:
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
        return self.llm.analyze_scenario(prompt)
