from pathlib import Path
from lxml import etree

from scenario_analysis.model.scenario import (
    Scenario, Entity, Story, Act, Maneuver, Event, Trigger, Condition
)


class OpenScenarioXMLParser:
    """
    Lightweight, analysis-oriented OpenSCENARIO 1.x XML parser.

    - Namespace-aware (with or without default namespace)
    - No simulator dependencies
    - No duplicate traversal
    - Designed for structural & semantic analysis
    """

    def __init__(self):
        self._namespace = None

    # ------------------------------------------------------------------
    # Namespace handling
    # ------------------------------------------------------------------

    def _detect_namespace(self, root):
        """
        Detect default XML namespace if present.
        """
        if root.tag.startswith("{"):
            self._namespace = root.tag.split("}")[0][1:]
        else:
            self._namespace = None

    def _tag(self, name: str) -> str:
        """
        Build a fully-qualified tag name if a namespace exists.
        """
        if self._namespace:
            return f"{{{self._namespace}}}{name}"
        return name

    def _find(self, element, tag):
        return element.find(self._tag(tag))

    def _findall(self, element, tag):
        return element.findall(self._tag(tag))

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def parse(self, filepath: str | Path) -> Scenario:
        filepath = Path(filepath)

        tree = etree.parse(str(filepath))
        root = tree.getroot()
        self._detect_namespace(root)

        # --------------------------------------------------------------
        # FileHeader
        # --------------------------------------------------------------

        header = self._find(root, "FileHeader")
        author = header.attrib.get("author", "unknown") if header is not None else "unknown"
        date = header.attrib.get("date", "unknown") if header is not None else "unknown"

        scenario = Scenario(
            name=filepath.stem,
            author=author,
            date=date,
        )
        
        # --------------------------------------------------------------
        # Entities
        # --------------------------------------------------------------

        entities_el = self._find(root, "Entities")
        if entities_el is not None:
            for obj in self._findall(entities_el, "ScenarioObject"):
                name = obj.attrib.get("name", "unknown")

                if self._find(obj, "Vehicle") is not None:
                    etype = "vehicle"
                elif self._find(obj, "Pedestrian") is not None:
                    etype = "pedestrian"
                else:
                    etype = "misc"

                scenario.entities.append(Entity(name=name, type=etype))
        
        # --------------------------------------------------------------
        # Storyboard
        # --------------------------------------------------------------

        storyboard = self._find(root, "Storyboard")
        
        # --------------------------------------------------------------
        # Init Speeds
        # --------------------------------------------------------------
        init_speeds = []
        if storyboard is not None:
            init_el = self._find(storyboard, "Init")
            if init_el is not None:
                actions_el = self._find(init_el, "Actions")
                if actions_el is not None:
                    for priv in self._findall(actions_el, "Private"):
                        for priv_action in self._findall(priv, "PrivateAction"):
                            long_act = self._find(priv_action, "LongitudinalAction")
                            if long_act is not None:
                                speed_act = self._find(long_act, "SpeedAction")
                                if speed_act is not None:
                                    target_speed = self._find(speed_act, "SpeedActionTarget")
                                    if target_speed is not None:
                                        abs_target = self._find(target_speed, "AbsoluteTargetSpeed")
                                        if abs_target is not None:
                                            val = abs_target.attrib.get("value")
                                            if val is not None:
                                                try:
                                                    init_speeds.append(float(val))
                                                except ValueError:
                                                    pass
        scenario.init_speeds = init_speeds

        if storyboard is not None:
            for story_el in self._findall(storyboard, "Story"):
                story = Story(name=story_el.attrib.get("name", "unnamed_story"))

                for act_el in self._findall(story_el, "Act"):
                    act = Act(name=act_el.attrib.get("name", "unnamed_act"))

                    for mg in self._findall(act_el, "ManeuverGroup"):
                        for man_el in self._findall(mg, "Maneuver"):
                            maneuver = Maneuver(
                                name=man_el.attrib.get("name", "unnamed_maneuver")
                            )

                            for event_el in self._findall(man_el, "Event"):
                                event_name = event_el.attrib.get("name", "unnamed_event")
                                trigger = self._parse_start_trigger(event_el)
                                
                                # Extract speeds from actions
                                speeds = []
                                action_el = self._find(event_el, "Action")
                                if action_el is not None:
                                    # Private actions (like routing/speed)
                                    for priv_action in self._findall(action_el, "PrivateAction"):
                                        long_act = self._find(priv_action, "LongitudinalAction")
                                        if long_act is not None:
                                            speed_act = self._find(long_act, "SpeedAction")
                                            if speed_act is not None:
                                                target_speed = self._find(speed_act, "SpeedActionTarget")
                                                if target_speed is not None:
                                                    abs_target = self._find(target_speed, "AbsoluteTargetSpeed")
                                                    if abs_target is not None:
                                                        val = abs_target.attrib.get("value")
                                                        if val is not None:
                                                            try:
                                                                speeds.append(float(val))
                                                            except ValueError:
                                                                pass

                                maneuver.events.append(
                                    Event(name=event_name, trigger=trigger, speeds=speeds)
                                )

                            act.maneuvers.append(maneuver)

                    story.acts.append(act)

                scenario.stories.append(story)

        return scenario

    # ------------------------------------------------------------------
    # Trigger parsing
    # ------------------------------------------------------------------

    def _parse_start_trigger(self, event_el) -> Trigger | None:
        start_trigger = self._find(event_el, "StartTrigger")
        if start_trigger is None:
            return None

        trigger = Trigger()

        for cond_group in self._findall(start_trigger, "ConditionGroup"):
            for cond_el in self._findall(cond_group, "Condition"):
                for child in cond_el:
                    cond_type = etree.QName(child).localname
                    trigger.conditions.append(
                        Condition(
                            type=cond_type,
                            attributes=dict(child.attrib)
                        )
                    )

        return trigger
