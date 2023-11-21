from typing import Any, Tuple
from axon.synapse.client import AxonSynapseClient
from axon.application.repositories import EventLockingRepository

from axon.adapter.payloads import payloadclass

from payloads import GameEvent, GameCommand


class GameEventRepository(EventLockingRepository[GameCommand, GameEvent, int]):
    def __init__(self, client: AxonSynapseClient) -> None:
        self.client = client

    async def fetch_events(self, c: GameCommand) -> list[Tuple[GameEvent, int]]:
        return await self.fetch_events_by_id(c.id)

    async def fetch_events_by_id(
        self, aggregate_id: str
    ) -> list[Tuple[GameEvent, int]]:
        response = await self.client.fetch_aggregate_events(aggregate_id)
        events = [
            (
                payloadclass.to_instance(r.payloadType, r.payload),
                r.sequenceNumber,
            )
            for r in response.items
        ]
        return events

    async def save(
        self, event: GameEvent, latest_version: int | None
    ) -> Tuple[GameEvent, int]:
        next_version = 0 if latest_version is None else latest_version + 1
        await self.client.append_event(
            aggregate_id=event.id,  # TODO: externalize
            aggregate_type="TicTacToe",
            payload_type=payloadclass.type_name(type(event)),
            payload=payloadclass.to_payload(event),
            sequence_number=next_version,
        )
        return (event, next_version)

    async def save_all(
        self, events: list[GameEvent], latest_version: int | None = None
    ) -> list[Tuple[GameEvent, int]]:
        results = []
        version = latest_version
        for event in events:
            event, version = await self.save(event, version)
            results.append((event, version))
        return results
