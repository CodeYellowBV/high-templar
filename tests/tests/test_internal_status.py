import json
from time import sleep
from unittest import TestCase
import websockets
import asyncio

from .utils.wiremock import set_bootstrap_response
from settings import WS_URI


class TestInternalStatus(TestCase):
    """
    Testing the internal status. Note this testcases depend on HT running in single thread mode
    """

    def test_open_connections(self):
        set_bootstrap_response({
            "allowed_rooms": [{
                "target": "message",
                "customer": "1"
            }]
        })

        async def run():
            async with websockets.connect(WS_URI) as ws:
                await ws.recv()
                status = await ws.send('{"type": "status"}')
                res = await ws.recv()

                res = json.loads(res)

                self.assertEqual(1, res['open_connections'])
                self.assertEqual(0, res['num_rooms'])

                async with websockets.connect(WS_URI) as ws2:
                    await ws2.recv()

                    status = await ws.send('{"type": "status"}')
                    res = await ws.recv()
                    res = json.loads(res)
                    self.assertEqual(2, res['open_connections'])
                    self.assertEqual(0, res['num_rooms'])

                status = await ws.send('{"type": "status"}')
                res = await ws.recv()
                res = json.loads(res)
                self.assertEqual(1, res['open_connections'])
                self.assertEqual(0, res['num_rooms'])

        asyncio.get_event_loop().run_until_complete(run())

    def test_room_autocloses_on_unsubscribe(self):
        set_bootstrap_response({
            "allowed_rooms": [{
                "target": "message",
                "customer": "1"
            }, {
                "target": "message",
                "customer": "2"
            }]
        })

        async def run():
            async with websockets.connect(WS_URI) as ws:
                await ws.recv()
                status = await ws.send('{"type": "status"}')
                res = await ws.recv()
                res = json.loads(res)
                self.assertEqual(0, res['num_rooms'])

                await ws.send(json.dumps({
                    "type": "subscribe",
                    "room": {
                        "target": "message",
                        "customer": "1"
                    },
                    "requestId": "71a518e6-ea5e-4d50-bc2c-6761470a22cf"
                }))
                await ws.recv()

                status = await ws.send('{"type": "status"}')
                res = await ws.recv()
                res = json.loads(res)
                self.assertEqual(1, res['num_rooms'])

                await ws.send(json.dumps({
                    "type": "subscribe", "room": {
                        "target": "message",
                        "customer": "2"
                    },
                    "requestId": "a9772e37-1840-4276-928f-8d75e7d0eda2"
                }))
                await ws.recv()

                status = await ws.send('{"type": "status"}')
                res = await ws.recv()
                res = json.loads(res)
                self.assertEqual(2, res['num_rooms'])

                await ws.send(json.dumps({
                    "type": "unsubscribe", "room": {
                        "target": "message",
                        "customer": "2"
                    },
                    "requestId": "a9772e37-1840-4276-928f-8d75e7d0eda2"
                }))
                await ws.recv()

                await ws.send('{"type": "status"}')
                res = await ws.recv()
                res = json.loads(res)
                print(">>>>", res)
                self.assertEqual(1, res['num_rooms'])

                await ws.send(json.dumps({
                    "type": "unsubscribe", "room": {
                        "target": "message",
                        "customer": "1"
                    },
                    "requestId": "71a518e6-ea5e-4d50-bc2c-6761470a22cf"
                }))
                await ws.recv()

                status = await ws.send('{"type": "status"}')
                res = await ws.recv()
                res = json.loads(res)
                self.assertEqual(0, res['num_rooms'])

        asyncio.get_event_loop().run_until_complete(run())

    def test_room_doesnt_close_if_second_subscription(self):
        set_bootstrap_response({
            "allowed_rooms": [{
                "target": "message",
                "customer": "1"
            }]
        })

        async def run():
            async with websockets.connect(WS_URI) as ws:
                await ws.recv()
                status = await ws.send('{"type": "status"}')
                res = await ws.recv()
                res = json.loads(res)
                self.assertEqual(0, res['num_rooms'])

                await ws.send(json.dumps({
                    "type": "subscribe",
                    "room": {
                        "target": "message",
                        "customer": "1"
                    },
                    "requestId": "4ee5112f-8940-4a22-9c29-77efdf1df3b3"
                }))
                await ws.recv()

                async with websockets.connect(WS_URI) as ws2:
                    await ws2.recv()

                    await ws2.send(json.dumps({
                        "type": "subscribe",
                        "room": {
                            "target": "message",
                            "customer": "1"
                        },
                        "requestId": "71a518e6-ea5e-4d50-bc2c-6761470a22cf"
                    }))

                    await ws2.recv()

                    await ws.send(json.dumps({
                        "type": "unsubscribe", "room": {
                            "target": "message",
                            "customer": "1"
                        }
                    }))
                    await ws.recv()

                    status = await ws.send('{"type": "status"}')
                    res = await ws.recv()
                    res = json.loads(res)
                    self.assertEqual(1, res['num_rooms'])

        asyncio.get_event_loop().run_until_complete(run())

    def test_auto_close_hubs_on_disconnect(self):
        set_bootstrap_response({
            "allowed_rooms": [{
                "target": "message",
                "customer": "1"
            }]
        })

        async def run():
            async with websockets.connect(WS_URI) as ws:
                await ws.recv()
                status = await ws.send('{"type": "status"}')
                res = await ws.recv()
                res = json.loads(res)
                self.assertEqual(0, res['num_rooms'])

                async with websockets.connect(WS_URI) as ws2:
                    await ws2.recv()

                    await ws2.send(json.dumps({
                        "type": "subscribe",
                        "room": {
                            "target": "message",
                            "customer": "1"
                        }
                    }))

                    await ws2.recv()

                status = await ws.send('{"type": "status"}')
                res = await ws.recv()
                res = json.loads(res)
                self.assertEqual(0, res['num_rooms'])

        asyncio.get_event_loop().run_until_complete(run())
