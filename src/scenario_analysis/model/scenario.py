# src/scenario_analysis/model/scenario.py

from dataclasses import dataclass, field
from typing import List, Dict


@dataclass
class Entity:
    name: str
    type: str


@dataclass
class Condition:
    type: str
    attributes: Dict[str, str]


@dataclass
class Trigger:
    conditions: List[Condition] = field(default_factory=list)


@dataclass
class Event:
    name: str
    trigger: Trigger | None


@dataclass
class Maneuver:
    name: str
    events: List[Event] = field(default_factory=list)


@dataclass
class Act:
    name: str
    maneuvers: List[Maneuver] = field(default_factory=list)


@dataclass
class Story:
    name: str
    acts: List[Act] = field(default_factory=list)


@dataclass
class Scenario:
    name: str
    author: str
    date: str
    entities: List[Entity] = field(default_factory=list)
    stories: List[Story] = field(default_factory=list)
