import json
from time import sleep
from unittest import TestCase
import websockets
import asyncio

from .utils.wiremock import set_bootstrap_response
from settings import WS_URI


class TestSubscribe(TestCase):
    """
    Simple test for setting up a websocket connection
    """

    def test_subscribe_to_room(self):
        set_bootstrap_response({
            "allowed_rooms": [{
                "target": "message",
                "customer": "1"
            }]
        })

        async def run():
            async with websockets.connect(WS_URI) as ws:
                await ws.recv()

                await ws.send(json.dumps({
                    "type": "subscribe",
                    "room": {
                        "target": "message",
                        "customer": "1"
                    },
                    "requestId": "9a2f3722-5c8f-11ea-bc55-0242ac130003"
                }))

                res = await ws.recv()

                res = json.loads(res)
                self.assertEqual("success", res['code'])

        asyncio.get_event_loop().run_until_complete(run())

    def test_subscribe_room_not_allowed(self):
        set_bootstrap_response({
            "allowed_rooms": [{
                "target": "message",
                "customer": "1"
            }]
        })

        async def run():
            async with websockets.connect(WS_URI) as ws:
                await ws.recv()

                await ws.send(json.dumps({
                    "type": "subscribe",
                    "room": {
                        "target": "foobar",
                        "customer": "2"
                    },
                    "requestId": "9a2f3722-5c8f-11ea-bc55-0242ac130003"
                }))

                res = await ws.recv()

                res = json.loads(res)
                self.assertEqual("error", res['code'])
                self.assertEqual("room-not-found", res['message'])

        asyncio.get_event_loop().run_until_complete(run())

    def test_subcribe_wildcard(self):
        set_bootstrap_response({
            "allowed_rooms": [{
                "target": 'reassignment-change-finished',
                "allocation": '*',
                "driver": '*',
                "truck": '*',
            }]
        })


        async def run():
            async with websockets.connect(WS_URI) as ws:
                await ws.recv()

                await ws.send(json.dumps({
                    "type": "subscribe",
                    "room": {
                        "target": 'reassignment-change-finished',
                        "allocation": 1,
                        "driver": '*',
                        "truck": '*',
                    },
                    "requestId": "9a2f3722-5c8f-11ea-bc55-0242ac130003"
                }))

                res = await ws.recv()

                res = json.loads(res)
                self.assertEqual("success", res['code'])

        asyncio.get_event_loop().run_until_complete(run())
