from scenario_analysis.model.scenario import Scenario
from collections import Counter

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
        
        trigger_types = []
        max_trigger_depth = 0 # In open scenario 1.x, triggers are usually flat lists of conditions, but we can count max conditions per trigger as depth proxy, or just sequential events. Let's use max conditions per trigger as "depth" for now, or just sequential events. We'll count max conditions per trigger.
        
        all_speeds = []
        
        if hasattr(scenario, 'init_speeds'):
            all_speeds.extend(scenario.init_speeds)

        for story in scenario.stories:
            num_acts += len(story.acts)
            for act in story.acts:
                num_maneuvers += len(act.maneuvers)
                for man in act.maneuvers:
                    num_events += len(man.events)
                    for ev in man.events:
                        if hasattr(ev, 'speeds'):
                            all_speeds.extend(ev.speeds)
                            
                        if ev.trigger:
                            num_triggers += 1
                            num_conditions += len(ev.trigger.conditions)
                            if len(ev.trigger.conditions) > max_trigger_depth:
                                max_trigger_depth = len(ev.trigger.conditions)
                            for cond in ev.trigger.conditions:
                                trigger_types.append(cond.type)

        features["num_acts"] = num_acts
        features["num_maneuvers"] = num_maneuvers
        features["num_events"] = num_events
        features["num_triggers"] = num_triggers
        features["num_conditions"] = num_conditions
        features["max_trigger_depth"] = max_trigger_depth
        
        # Kinematics
        features["max_speed_ms"] = max(all_speeds) if all_speeds else 0.0
        features["avg_speed_ms"] = sum(all_speeds) / len(all_speeds) if all_speeds else 0.0
        
        # Count types
        type_counts = Counter(trigger_types)
        features["trigger_types"] = dict(type_counts)

        return features
