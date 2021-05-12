import json
from unittest import TestCase
import websockets
import asyncio

from .utils.rabbitmq import send_trigger
from .utils.wiremock import set_bootstrap_response
from settings import WS_URI
# from time import time

class TestSubscribe(TestCase):
    """
    Simple test for setting up a websocket connection.

    TODO: Somehow measure performance.
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
            async with websockets.connect(WS_URI) as wsx:
                await wsx.recv()

                await wsx.send('{"type": "status"}')
                status = json.loads(await wsx.recv())
                self.assertEqual(0, status['num_rooms'])
                self.assertEqual(1, status['open_connections'])

                # start1 = time()
                async with websockets.connect(WS_URI) as ws:
                    await ws.recv()

                    # start = time()
                    for i in range(NUM_ROOMS):
                        # print(f'++++ {i}')
                        await ws.send(json.dumps({
                            "type": "subscribe",
                            "room": {
                                "target": "message",
                                "customer": f"{i}"
                            },
                            "requestId": f"{i}"
                        }))

                        res = json.loads(await ws.recv())
                        self.assertEqual("success", res['code'])

                    # print(f'subscribe done in {time() - start}')

                    # start = time()
                    await wsx.send('{"type": "status"}')
                    status = json.loads(await wsx.recv())
                    self.assertEqual(NUM_ROOMS, status['num_rooms'])
                    self.assertEqual(2, status['open_connections'])

                    for i in range(NUM_ROOMS):
                        send_trigger({
                            "rooms": [
                                {
                                    "target": "message",
                                    "customer": f"{i}"
                                }

                            ],
                            "data": {
                                "customer": f"{i}"
                            }
                        })
                        res = await ws.recv()

                    # print(f'trigger done in {time() - start}')

                # print(f'user done in {time() - start1}')
                await wsx.send('{"type": "status"}')
                status = json.loads(await wsx.recv())
                self.assertEqual(0, status['num_rooms'])
                self.assertEqual(1, status['open_connections'])

        asyncio.get_event_loop().run_until_complete(run())
