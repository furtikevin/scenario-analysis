from scenario_analysis.model.scenario import Scenario


class BasicStatsExtractor:
    """
    Deterministic structural feature extraction.
    """

    def extract(self, scenario: Scenario) -> dict:
        features = {}

        features["num_entities"] = len(scenario.entities)
        features["num_stories"] = len(scenario.stories)

        num_acts = 0
        num_maneuvers = 0
        num_events = 0
        num_triggers = 0
        num_conditions = 0

        for story in scenario.stories:
            num_acts += len(story.acts)
            for act in story.acts:
                num_maneuvers += len(act.maneuvers)
                for man in act.maneuvers:
                    num_events += len(man.events)
                    for ev in man.events:
                        if ev.trigger:
                            num_triggers += 1
                            num_conditions += len(ev.trigger.conditions)

        features["num_acts"] = num_acts
        features["num_maneuvers"] = num_maneuvers
        features["num_events"] = num_events
        features["num_triggers"] = num_triggers
        features["num_conditions"] = num_conditions

        return features
