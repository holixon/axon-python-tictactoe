from pprint import pprint
from axon.domain.view import IView
from adapter.game_event_repository import GameEventRepository
from domain.game.state import TicTacToeState as GameState
from payloads import *


QTable = dict[str, float]


class GameTrainer:  # IView[QTable, GameEvent]
    def __init__(
        self, Q, alpha=0.2, gamma=0.75, repository: GameEventRepository = None
    ) -> None:
        self.repository = repository
        self.states = {}
        self.Q = Q
        self.alpha = alpha
        self.gamma = gamma

    async def __call__(self, event: GameFinishedEvent, _) -> QTable:
        return await self.handle(event)

    async def handle(self, event: GameEvent) -> QTable:
        actions = self.states.get(event.id, [])
        match event:
            case MovePlayedEvent(action=action):
                self.states[event.id] = actions + [action]
            case GameFinishedEvent(winner=winner):
                actions = self.states[event.id]
                self.train(actions=actions, winner=winner)
            case _:
                print(f"Nothing found for {event}")

    def train(self, actions, winner):
        state = GameState()
        players = 1, -1
        for i, action in enumerate(actions):
            state = state.move(action)
            qvalue = self.Q.get(str(state)) or 0
            reward = 999 if i > (len(actions) - 3) else 0
            decay_reward = ((i + 1) / len(actions)) ** 2
            if players[i % 2] != winner:
                reward = -1 * reward
                decay_reward = -0.5 * decay_reward
            TD = reward + self.gamma * decay_reward - qvalue
            qvalue = qvalue + self.alpha * TD
            self.Q[str(state)] = qvalue
