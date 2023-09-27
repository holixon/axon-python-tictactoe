from abc import ABC, abstractmethod
from random import randint, random
from numpy import argmax


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


class ConsolePlayer(Player):
    def next_action(self, state):
        actions = state.actions()
        while True:
            try:
                print(repr(state))
                action = input(f"Action [{actions}]: ")
                action = int(action)
                if action in actions:
                    return action
            except Exception:
                pass


class MiniMaxPlayer(IndecisivePlayer):
    def __init__(self, lookahead):
        assert lookahead > 0
        self.lookahead = lookahead

    def next_actions(self, state):
        moves, _ = self.value(state, self.lookahead)
        return moves

    def value(self, state, lookahead):
        if lookahead == 0 or state.gameover():
            return [], 1.0 * state.winner() * (lookahead + 1)
        behaviour = max if state.player() == 1 else min
        return self.minimax(state, behaviour, lookahead)

    def minimax(self, state, behaviour, lookahead):
        moves, res = [], -10000 * state.player()
        for cell in state.actions():
            _, v = self.value(state.move(cell), lookahead - 1)
            if res == v:
                moves.append(cell)
            elif behaviour(res, v) == v:
                moves, res = [cell], v
        return moves, res


class QPlayer(IndecisivePlayer):
    def __init__(self, Q) -> None:
        self.Q = Q
        self.counter = make_counter()
        self.visited = make_counter()

    def next_actions(self, state):
        actions = state.actions()
        values = [self.Q.get(state.move(action)) or 0 for action in actions]
        vactions = [a for a, v in zip(actions, values) if v > 0]
        # return vactions if len(vactions) > 0 and random() > 0.2 else actions
        if sum(e * e for e in state.cells) < 2:
            return actions
        if random() < 0.05:
            vactions = [a for a, v in zip(actions, values) if v > 0]
            return vactions if len(vactions) > 0 else actions
        index = argmax(values)
        result = [
            action for action, value in zip(actions, values) if value == values[index]
        ]
        self.counter()
        if values[index] > 0:
            self.visited()
        # print(f"{result=} {values[index]=}")
        return result

    def next_actions__(self, state):
        actions = state.actions()
        values = [self.Q.get(state, action) or 0 for action in actions]
        if sum(e * e for e in state.cells) < 4:
            vactions = [a for a, v in zip(actions, values) if v > 0]
            return vactions if len(vactions) > 0 else actions
        index = argmax(values)
        result = [
            action for action, value in zip(actions, values) if value == values[index]
        ]
        self.counter()
        if values[index] > 0:
            self.visited()
        # print(f"{result=} {values[index]=}")
        return result

    def next_actions_(self, state):
        actions = state.actions()
        values = [self.Q.get(f"{state}:{action}") or 0 for action in actions]
        if sum(e * e for e in state.cells) < 4:
            vactions = [a for a, v in zip(actions, values) if v > 0]
            return vactions if len(vactions) > 0 else actions
        index = argmax(values)
        result = [
            action for action, value in zip(actions, values) if value == values[index]
        ]
        self.counter()
        if values[index] > 0:
            self.visited()
        # print(f"{result=} {values[index]=}")
        return result


def make_counter():
    i = [0]

    def _c(inc=True):
        if inc:
            i[0] = i[0] + 1
        return i[0]

    return _c
