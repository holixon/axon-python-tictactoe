import uuid
import json
from pprint import pprint
from aiohttp import web
import aiohttp_jinja2
import jinja2
from axon.adapter.payloads import payload_from_object
from axon.synapse_client import AxonSynapseClient
from domain.game.state import TicTacToeState as GameState
from domain.game.players import RandomPlayer
from domain.game.simulation import play, simulate
from payloads import *


class MessageGateway:
    def __init__(self, client) -> None:
        self.client = client


class GameCommandGateway(MessageGateway):
    async def dispatch(self, command: GameCommand):
        payload_type = command._payload_type
        client = self.client
        if client is None or payload_type is None:
            raise ValueError(f"Invalid State {client}, {payload_type}")

        return await client.dispatch_command(
            command_name=payload_type,
            payload_type=payload_type,
            payload=payload_from_object(command),
        )


class GameQueryGateway(MessageGateway):
    async def query(self, query: GameQuery):
        payload_type = query._payload_type
        client = self.client
        if client is None or payload_type is None:
            raise ValueError(f"Invalid State {client}, {payload_type}")
        return await client.publish_query(
            query_name=payload_type,
            payload_type=payload_type,
            payload=payload_from_object(query),
        )


@aiohttp_jinja2.template("index.jinja2")
async def index(request):
    return {"id": uuid.uuid4()}


async def move(request):
    dispatch = request.app["CommandGateway"].dispatch
    payload = await request.json()
    print(payload)
    command = PlayMoveCommand(**payload)
    text = await dispatch(command)
    print("TEXT", text)
    result = json.loads(text)
    pprint(result)
    response = {
        "action": command.action,
        "gameover": len(result) > 1,
    }
    if response["gameover"]:
        response["winner"] = result[1][0]["winner"]
    return web.json_response(response)


async def recommend(request):
    query = request.app["QueryGateway"].query
    state = await request.json()
    pprint(state)
    result = await query(RecommendedActionsQuery(**state))
    pprint(result)
    return web.json_response(result)


async def simulate_plays(request):
    dispatch = request.app["CommandGateway"].dispatch
    payload = await request.json()
    pprint(payload)
    response = await dispatch(SimulateGameCommand(count=payload["count"]))
    return web.json_response(response)


async def on_startup(app):
    print("on_startup")
    client = AxonSynapseClient()
    app["CommandGateway"] = GameCommandGateway(client)
    app["QueryGateway"] = GameQueryGateway(client)
    app["Client"] = client


async def on_cleanup(app):
    print("on_cleanup")


async def main():
    app = web.Application()
    aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader("templates"))
    app.router.add_get("/", index)
    app.router.add_post("/play", move)
    app.router.add_post("/recommend", recommend)
    app.router.add_post("/simulate", simulate_plays)
    app.router.add_static("/images", "templates/images")
    app.on_startup.append(on_startup)
    app.on_cleanup.append(on_cleanup)
    return app


if __name__ == "__main__":
    web.run_app(main(), port=8881)
