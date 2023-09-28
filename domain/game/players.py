from abc import ABC, abstractmethod
from random import randint


class Player(ABC):
    @abstractmethod
    def next_action(self, state):
        ...


class IndecisivePlayer(Player):
    def next_action(self, state):
        moves = self.next_actions(state)
        return moves[randint(0, len(moves) - 1)]

    @abstractmethod
    def next_actions(self, state):
        ...


class RandomPlayer(IndecisivePlayer):
    def next_actions(self, state):
        return state.actions()
