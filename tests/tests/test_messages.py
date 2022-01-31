import json
from time import sleep
from unittest import TestCase
import websockets
import asyncio

from .utils.rabbitmq import send_trigger
from .utils.wiremock import set_bootstrap_response
from settings import WS_URI


class TestMessages(TestCase):
    """
    Test that messages of HT are correctly send back to the end user
    """

    def test_simple_subscribe_gets_message(self):
        """
        Simple test for setting up a websocket connection
        """

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
                    }
                }))
                await ws.recv()

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

                res = await ws.recv()
                res = json.loads(res)
                del res['requestId']

                self.assertEquals(data, res)

        asyncio.get_event_loop().run_until_complete(run())

    def test_two_websocket_connections(self):
        set_bootstrap_response({
            "allowed_rooms": [{
                "target": "message",
                "customer": "1"
            }]
        })

        async def run():
            async with websockets.connect(WS_URI) as ws, \
                    websockets.connect(WS_URI) as ws2:
                await ws.recv()
                await ws2.recv()

                await ws.send(json.dumps({
                    "type": "subscribe",
                    "room": {
                        "target": "message",
                        "customer": "1"
                    }
                }))
                await ws.recv()

                await ws2.send(json.dumps({
                    "type": "subscribe",
                    "room": {
                        "target": "message",
                        "customer": "1"
                    }
                }))
                await ws2.recv()

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

                res = await ws.recv()
                res = json.loads(res)
                del res['requestId']
                self.assertEquals(data, res)

                res = await ws2.recv()
                res = json.loads(res)
                del res['requestId']
                self.assertEquals(data, res)

        asyncio.get_event_loop().run_until_complete(run())

    def test_subscribe_all_gets_message(self):
        set_bootstrap_response({
            "allowed_rooms": [{
                "target": "message",
                "customer": "*"
            }]
        })

        async def run():
            async with websockets.connect(WS_URI) as ws:
                await ws.recv()

                await ws.send(json.dumps({
                    "type": "subscribe",
                    "room": {
                        "target": "message",
                        "customer": "*"
                    }
                }))
                await ws.recv()

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

                res = await ws.recv()
                res = json.loads(res)
                del res['requestId']

                self.assertEquals(data, res)

        asyncio.get_event_loop().run_until_complete(run())

    def test_subscribe_no_permission_no_message(self):
        set_bootstrap_response({
            "allowed_rooms": [{
                "target": "message",
                "customer": "2"
            }]
        })

        async def run():
            async with websockets.connect(WS_URI) as ws:
                await ws.recv()

                await ws.send(json.dumps({
                    "type": "subscribe",
                    "room": {
                        "target": "message",
                        "customer": "2"
                    }
                }))
                await ws.recv()

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

                # check that we are not notified after two seconds
                with self.assertRaises(asyncio.TimeoutError):
                    await asyncio.wait_for(ws.recv(), timeout=2)

        asyncio.get_event_loop().run_until_complete(run())
