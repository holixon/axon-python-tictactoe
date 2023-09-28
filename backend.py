import os
import uuid
import socket
from pprint import pprint
from aiohttp import web

from axon.adapter.handlers import (
    event_message_handler,
    command_message_handler,
    query_message_handler,
)

from axon.application.aggregates import EventSourcingLockingAggregate

from adapter.game_event_repository import GameEventRepository
from application.trainer import GameTrainer
from domain.decider import TicTacToeDecider
from domain.game.state import TicTacToeState as GameState
from domain.game.simulation import simulate

from payloads import *

from axon.synapse_client import AxonSynapseClient
from axon.adapter.handlers import CommandMessage


class GameAggregate(
    EventSourcingLockingAggregate[GameCommand, GameState, GameEvent, int]
):
    pass


def simulation_handler(repository: GameEventRepository):
    @command_message_handler
    async def handle(command: SimulateGameCommand, _):
        for history, winner in simulate(GameState(), command.count):
            game_id = str(uuid.uuid4())
            events = [
                MovePlayedEvent(id=game_id, action=play.action) for play in history
            ]
            events.append(GameFinishedEvent(id=game_id, winner=winner))
            await repository.save_all(events)
        # return web.json_response({})

    return handle


class RecommendationQueryHandler:
    def __init__(self, Q: dict[str, float]) -> None:
        self.Q = Q

    async def __call__(self, query: RecommendedActionsQuery, _) -> list[float] | None:
        match query:
            case RecommendedActionsQuery():
                state = GameState(query.state)
                values = {a: self.Q.get(str(state.move(a))) for a in state.actions()}
                result = [values.get(a) or 0 for a in range(0, 9)]
                # pprint(self.Q)
                pprint(result)
                result = self.scale(result)
                pprint(result)
                return result
            case _:
                print(f"Nothing found for {query}")
        return None

    def scale(self, values):
        # minx = min(*values)
        total = sum(abs(e) for e in values)
        if total == 0:
            return values
        return [v / total for v in values]


def routes(client: AxonSynapseClient):
    # state_repository = GiftCardViewStateRepository()
    event_repository = GameEventRepository(client)
    decider = TicTacToeDecider()
    aggregate = GameAggregate(
        repository=event_repository,
        decider=decider,
    )
    Q = {}
    return [
        web.post(
            "/commands",
            command_message_handler(aggregate),
        ),
        web.post(
            "/simulate",
            simulation_handler(event_repository),
        ),
        web.post(
            "/events",
            event_message_handler(
                GameTrainer(Q=Q),
            ),
        ),
        web.post(
            "/queries",
            query_message_handler(
                RecommendationQueryHandler(Q=Q),
            ),
        ),
    ]

    # web.run_app(app, port=port)


async def register_handlers(client: AxonSynapseClient):
    hostname = os.getenv("CALLBACK_HOST", socket.gethostname())
    callback_url = f"http://{hostname}:8888"
    # callback_url = f"http://localhost:8888"
    uuids = "0274567e-1742-4446-b649"
    kwargs = dict(
        client_id="python-ttt-7d78946494-p8ttt",
        component_name="TicTacToe",
    )
    types = lambda *l: [e._payload_type for e in l]

    response = await client.register_event_handler(
        handler_id=f"events-{uuids}",
        callback_endpoint=f"{callback_url}/events",
        names=types(
            MovePlayedEvent,
            GameFinishedEvent,
        ),
        **kwargs,
    )
    pprint(response)
    response = await client.register_command_handler(
        handler_id=f"commands-{uuids}",
        callback_endpoint=f"{callback_url}/commands",
        names=types(
            PlayMoveCommand,
        ),
        **kwargs,
    )
    pprint(response)
    response = await client.register_command_handler(
        handler_id=f"simulation-{uuids}",
        callback_endpoint=f"{callback_url}/simulate",
        names=types(
            SimulateGameCommand,
        ),
        **kwargs,
    )
    pprint(response)
    response = await client.register_query_handler(
        handler_id=f"query-{uuids}",
        callback_endpoint=f"{callback_url}/queries",
        names=types(
            RecommendedActionsQuery,
            # FetchCardSummariesQuery,
        ),
        **kwargs,
    )
    pprint(response)


async def main():
    app = web.Application()
    client = AxonSynapseClient()
    await register_handlers(client=client)
    app.add_routes(routes(client))
    return app


if __name__ == "__main__":
    web.run_app(main(), port=8888)
