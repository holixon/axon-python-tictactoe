from typing import Counter


symbols = [".", "X", "O"]


class State:
    def __init__(self, cells, cols, rows, rules):
        self._cols = cols
        self._rows = rows
        self._rules = rules
        self.cells = cells.copy() if cells else [0] * (cols * rows)

    def actions(self):
        return [i for i, c in enumerate(self.cells) if c == 0]

    def player(self):
        return [1, -1][sum(self.cells)]

    def gameover(self):
        return self.winner() != 0 or len(self.actions()) == 0

    def winner(self):
        strikes = list(self.strikes())
        if len(strikes) == 0:
            return 0
        _, winners = zip(*strikes)
        value, _ = Counter(winners).most_common(1)[0]
        return value

    def strikes(self):
        for rule in self._rules:
            score = sum(self.cells[i] for i in rule)
            if abs(score) == len(rule):
                yield rule, self.cells[rule[0]]

    def rows(self):
        return [
            self.cells[i * self._cols : (i + 1) * self._cols] for i in range(self._rows)
        ]

    def cols(self):
        return [self.cells[i :: self._cols] for i in range(self._rows)]

    def move(self, action):
        state = self.__class__(self.cells)
        if state.cells[action] != 0:
            raise ValueError(f"{state.cells} invalid move {action}")
        state.cells[action] = state.player()
        return state

    def __str__(self):
        return "".join(symbols[i] for i in self.cells)

    def __repr__(self):
        rows = [" ".join(symbols[i] for i in row) for row in self.rows()]
        board = "\n".join(rows)
        if self.winner() != 0:
            msg = f"Winner is {symbols[self.winner()]}"
        elif self.gameover():
            msg = "It's a draw"
        else:
            msg = f"It's {symbols[self.player()]}'s turn"

        return f"\n{board}\n\n{msg}\n"


def make_rules(cols, rows, score):
    rules = []
    lim_rows = rows - score + 1
    lim_cols = cols - score + 1

    def idx(c, r):
        return r * cols + c

    # Vertical
    for c in range(cols):
        for r in range(lim_rows):
            rules.append([idx(c, r + j) for j in range(score)])

    # Horizontal
    for r in range(rows):
        for c in range(lim_cols):
            rules.append([idx(c + j, r) for j in range(score)])

    # Diagonal
    for r in range(lim_rows):
        for c in range(lim_cols):
            rules.append([idx(c + j, r + j) for j in range(score)])
            rules.append([idx(c + j, r - j + score - 1) for j in range(score)])
    return rules

tictactoe_rules = make_rules(cols=3, rows=3, score=3)


class TicTacToeState(State):
    def __init__(self, cells=None):
        super().__init__(cells, cols=3, rows=3, rules=tictactoe_rules)
