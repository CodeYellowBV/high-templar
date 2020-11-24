import json
from time import sleep
from unittest import TestCase
import websockets
import asyncio

from .utils.wiremock import set_bootstrap_response
from settings import WS_URI


class TestSetupConnection(TestCase):
    """
    Simple test for setting up a websocket connection
    """

    def test_subscribe_ws_gives_rooms(self):
        set_bootstrap_response({})

        async def run():
            async with websockets.connect(WS_URI) as ws:
                res = await ws.recv()
                res = json.loads(res)


                # We do not have access to any rooms
                self.assertEqual({"is_authorized": True, "allowed_rooms": []}, res)

        asyncio.get_event_loop().run_until_complete(run())

    def test_subscribe_ws_not_logged_in_gives_not_logged_in(self):
        set_bootstrap_response(None)

        async def run():
            async with websockets.connect(WS_URI) as ws:
                res = await ws.recv()
                res = json.loads(res)


                # We do not have access to any rooms
                self.assertEqual({"is_authorized": False}, res)

                sleep(0.1)
                with self.assertRaises(websockets.ConnectionClosedOK):
                    res = await ws.recv()

        asyncio.get_event_loop().run_until_complete(run())

    def test_subscribe_ws_gives_authenticated_rooms(self):
        set_bootstrap_response({
            "allowed_rooms": [{
                "target": "foo"
            }]
        })

        async def run():
            async with websockets.connect(WS_URI) as ws:
                res = await ws.recv()

                # We do not have access to any rooms
                res = json.loads(res)
                self.assertEqual({"is_authorized": True, "allowed_rooms": [{
                    "target": "foo"
                }]}, res)

        asyncio.get_event_loop().run_until_complete(run())

    def test_not_authorized_on_not_parsable_permission(self):
        set_bootstrap_response({
            "allowed_rooms": ["foo"]
        })

        async def run():
            async with websockets.connect(WS_URI) as ws:
                response = json.loads(await ws.recv())
                self.assertFalse(response['is_authorized'])

        asyncio.get_event_loop().run_until_complete(run())

    def test_ping_pong(self):
        set_bootstrap_response({})

        async def run():
            async with websockets.connect(WS_URI) as ws:
                allowed_rooms = await ws.recv()
                await ws.send('ping')
                self.assertEqual('pong', await ws.recv())

        asyncio.get_event_loop().run_until_complete(run())

    def test_unsupported_action_gives_error(self):
        set_bootstrap_response({})

        async def run():
            async with websockets.connect(WS_URI) as ws:
                allowed_rooms = await ws.recv()
                await ws.send('{"type": "foobar"}')
                response = json.loads(await ws.recv())
                self.assertEqual("error", response['code'])
                self.assertEqual("message-type-not-allowed", response['message'])

        asyncio.get_event_loop().run_until_complete(run())

    def test_non_json_message_gives_error(self):
        set_bootstrap_response({})

        async def run():
            async with websockets.connect(WS_URI) as ws:
                allowed_rooms = await ws.recv()
                await ws.send('geen json')
                response = json.loads(await ws.recv())
                self.assertEqual("error", response['code'])
                self.assertEqual("non-json-message", response['message'])

        asyncio.get_event_loop().run_until_complete(run())
