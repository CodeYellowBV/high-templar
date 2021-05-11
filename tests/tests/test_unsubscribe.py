import json
from time import sleep
from unittest import TestCase
import websockets
import asyncio

from .utils.wiremock import set_bootstrap_response
from settings import WS_URI


class TestUnSubscribe(TestCase):
    """
    Simple test for setting up a websocket connection
    """

    def test_unsubscribe_to_room(self):
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
                    "requestId": "1ba319b0-b720-4c24-991a-40be402ba64f"
                }))

                await ws.recv()

                await ws.send(json.dumps({
                    "type": "unsubscribe",
                    "requestId": "1ba319b0-b720-4c24-991a-40be402ba64f"
                }))

                res = await ws.recv()
                res = json.loads(res)
                self.assertEqual("success", res['code'])

        asyncio.get_event_loop().run_until_complete(run())

    def test_unsubscribe_to_room_error_not_subscribed(self):
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
                    "type": "unsubscribe",
                    "room": {
                        "target": "message",
                        "customer": "1"
                    },
                    "requestId": "1ba319b0-b720-4c24-991a-40be402ba64f"
                }))

                res = await ws.recv()
                res = json.loads(res)
                self.assertEqual("error", res['code'])
                self.assertEqual("not-subscribed", res['message'])

        asyncio.get_event_loop().run_until_complete(run())
