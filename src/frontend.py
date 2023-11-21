from os.path import dirname, abspath, join
import uuid
import json
from pprint import pprint
from aiohttp import web
import aiohttp_jinja2
import jinja2
from axon.adapter.payloads import payloadclass
from axon.synapse.client import AxonSynapseClient

from payloads import *


class MessageGateway:
    def __init__(self, client) -> None:
        self.client = client


class GameCommandGateway(MessageGateway):
    async def dispatch(self, command: GameCommand):
        payload_type = payloadclass.type_name(type(command))
        client = self.client
        if client is None or payload_type is None:
            raise ValueError(f"Invalid State {client}, {payload_type}")

        return await client.dispatch_command(
            command_name=payload_type,
            payload_type=payload_type,
            payload=payloadclass.to_payload(command),
        )


class GameQueryGateway(MessageGateway):
    async def query(self, query: GameQuery):
        payload_type = payloadclass.type_name(type(query))
        client = self.client
        if client is None or payload_type is None:
            raise ValueError(f"Invalid State {client}, {payload_type}")
        return await client.publish_query(
            query_name=payload_type,
            payload_type=payload_type,
            payload=payloadclass.to_payload(query),
        )


@aiohttp_jinja2.template("index.jinja2")
async def index(request):
    return {"id": uuid.uuid4()}


async def move(request):
    command = PlayMoveCommand(**(await request.json()))
    result = json.loads(await request.app["CommandGateway"].dispatch(command))
    payload = {
        "action": command.action,
        "gameover": len(result) > 1,
    }
    if payload["gameover"]:
        payload["winner"] = result[1][0]["winner"]
    return web.json_response(payload)


async def recommend(request):
    return web.json_response(
        await request.app["QueryGateway"].query(
            RecommendedActionsQuery(**(await request.json()))
        )
    )


async def simulate_plays(request):
    return web.json_response(
        await request.app["CommandGateway"].dispatch(
            SimulateGameCommand(**(await request.json()))
        )
    )


async def on_cleanup_ctx(app):
    print("on_cleanup_ctx (SETUP)")
    async with AxonSynapseClient() as client:
        app["CommandGateway"] = GameCommandGateway(client)
        app["QueryGateway"] = GameQueryGateway(client)
        app["Client"] = client
        yield
    print("on_cleanup_ctx (CLEANUP)")


async def main():
    app = web.Application()
    tpl_dir = join(dirname(abspath(__file__)), "templates")
    print(f"{tpl_dir=}")
    aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader(tpl_dir))
    app.router.add_get("/", index)
    app.router.add_post("/play", move)
    app.router.add_post("/recommend", recommend)
    app.router.add_post("/simulate", simulate_plays)
    app.router.add_static("/assets", join(tpl_dir, "assets"))
    app.cleanup_ctx.append(on_cleanup_ctx)
    return app


if __name__ == "__main__":
    web.run_app(main(), port=8881)
