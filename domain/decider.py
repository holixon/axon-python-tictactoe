from payloads import *
from axon.domain.decider import IDecider
from domain.game.state import TicTacToeState as GameState


class TicTacToeDecider(IDecider[GameCommand, GameState, GameEvent]):
    def evolve(self, state: GameState | None, event: GameEvent) -> GameState:
        state = state or self.initial_state
        match event:
            case MovePlayedEvent():
                return state.move(event.action)
            case GameFinishedEvent():
                return state
            case _:
                print(f"Nothing found for {event}")
        raise ValueError(f"Cannot handle event {event}, state: {state}")

    def decide(self, command: GameCommand, state: GameState | None) -> list[GameEvent]:
        # print("DECIDE", type(command), repr(state))
        match command:
            case PlayMoveCommand():
                if not state.gameover() and (command.action in state.actions()):
                    events = [MovePlayedEvent(id=command.id, action=command.action)]
                    newstate = state.move(command.action)
                    if newstate.gameover():
                        events.append(
                            GameFinishedEvent(id=command.id, winner=newstate.winner())
                        )
                    return events
                else:
                    raise ValueError(f"Invalid action {command.action}")
            case _:
                print(f"Nothing found for {command}")
        return []

    @property
    def initial_state(self) -> GameState | None:
        return GameState()
