from types import SimpleNamespace
from domain.game.players import RandomPlayer


def play(state, player1=None, player2=None):
    players = {1: player1 or RandomPlayer(), -1: player2 or RandomPlayer()}
    states = []
    while not state.gameover():
        player = players[state.player()]
        action = player.next_action(state)
        state = state.move(action)
        states.append(SimpleNamespace(action=action, state=state))
    return states, state.winner()


def simulate(state, play_count, player1=None, player2=None):
    import click

    label = f"Simulating {play_count} games..."
    tics = max(1, int(play_count / 100))
    with click.progressbar(label=label, length=play_count) as bar:
        for i in range(play_count):
            states, winner = play(state, player1, player2)
            if winner != 0:
                yield (states, winner)
            if (i + 1) % tics == 0:
                bar.update(tics)
