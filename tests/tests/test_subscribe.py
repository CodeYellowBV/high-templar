import json
from time import sleep
from unittest import TestCase
import websockets
import asyncio

from .wiremock import set_bootstrap_response
from settings import WS_URI


class TestPublish(TestCase):
    def test_subscribe_ws_gives_rooms(self):


        set_bootstrap_response({})

        async def run():
            async with websockets.connect(WS_URI) as ws:
                res = await ws.recv()


                # We do not have access to any rooms
                self.assertEqual({"is_authorized": True, "allowed_rooms": []}, json.loads(res))

        asyncio.get_event_loop().run_until_complete(run())

    def test_subscribe_ws_not_logged_in_gives_not_logged_in(self):

        set_bootstrap_response(None)

        async def run():
            async with websockets.connect(WS_URI) as ws:
                res = await ws.recv()

                # We do not have access to any rooms
                self.assertEqual({"is_authorized": False}, json.loads(res))

                sleep(0.1)
                with self.assertRaises(websockets.ConnectionClosedError):
                    res = await ws.recv()

        asyncio.get_event_loop().run_until_complete(run())

