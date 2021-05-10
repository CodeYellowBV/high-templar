import json
from time import sleep
from unittest import TestCase
import websockets
import asyncio

from .utils.rabbitmq import send_trigger
from .utils.wiremock import set_bootstrap_response
from settings import WS_URI


class TestSubscribe(TestCase):
    """
    Simple test for setting up a websocket connection
    """

    def test_subscribe_to_room(self):

        NUM_ROOMS = 1500

        set_bootstrap_response({
            "allowed_rooms": [{
                "target": "message",
                "customer": f"{i}"
            } for i in range(NUM_ROOMS)]
        })

        async def run():
            async with websockets.connect(WS_URI) as ws:
                await ws.recv()

                for i in range(NUM_ROOMS):
                    await ws.send(json.dumps({
                        "type": "subscribe",
                        "room": {
                            "target": "message",
                            "customer": f"{i}"
                        },
                        "requestId": "9a2f3722-5c8f-11ea-bc55-0242ac130003"
                    }))

                    res = await ws.recv()

                data = {
                    "foo": "bar"
                }

                send_trigger({
                    "rooms": [
                        {
                            "target": "message",
                            "customer": "1"
                        }

                    ],
                    "data": data
                })

                res = json.loads(res)
                self.assertEqual("success", res['code'])

        asyncio.get_event_loop().run_until_complete(run())