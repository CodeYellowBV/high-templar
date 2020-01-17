from unittest import TestCase
import websockets
import asyncio


class TestPublish(TestCase):
    def test_subscribe_ws(self):

        async def run():
            uri = 'ws://127.0.0.1:8000/ws/'
            async with websockets.connect(uri) as ws:
                await ws.send('ping')

                greeting = await ws.recv()
        asyncio.get_event_loop().run_until_complete(run())