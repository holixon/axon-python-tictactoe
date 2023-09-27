from dataclasses import dataclass
from axon.adapter.payloads import payloadclass


@payloadclass("PlayMoveCommand")
@dataclass
class PlayMoveCommand:
    id: str
    action: int


@payloadclass("SimulateGameCommand")
@dataclass
class SimulateGameCommand:
    count: int


@payloadclass("MovePlayedEvent")
@dataclass
class MovePlayedEvent:
    id: str
    action: int


@payloadclass("GameFinishedEvent")
@dataclass
class GameFinishedEvent:
    id: str
    winner: int


@payloadclass("RecommendedActionsQuery")
@dataclass
class RecommendedActionsQuery:
    state: list[int]


GameEvent = MovePlayedEvent | GameFinishedEvent
GameCommand = PlayMoveCommand
GameQuery = RecommendedActionsQuery
