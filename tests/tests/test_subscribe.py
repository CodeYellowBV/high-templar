import json
from unittest import TestCase
import websockets
import asyncio
from wiremock.constants import Config
from wiremock.client import Mapping, Mappings
from wiremock.resources.mappings import MappingRequest, HttpMethods, MappingResponse

Config.base_url = 'http://127.0.0.1:8080/__admin'

mapping = Mapping(
    priority=100,
    request=MappingRequest(
        method=HttpMethods.GET,
        url='/api/bootstrap/'
    ),
    response=MappingResponse(
        status=200,
        body=json.dumps({"data": [], "with": {},
                         "with_mapping": {}, "with_related_name_mapping": {}, "meta": {},
                         "debug": {"request_id": ""}})
    ),
    persistent=False,
)
mapping = Mappings.create_mapping(mapping=mapping)


class TestPublish(TestCase):
    def test_subscribe_ws_gives_rooms(self):
        uri = 'ws://localhost:5000/ws/'

        async def run():
            async with websockets.connect(uri) as ws:
                res = await ws.recv()

                print(res)

        asyncio.get_event_loop().run_until_complete(run())

        # asyncio.get_event_loop().run_until_complete(run2())
