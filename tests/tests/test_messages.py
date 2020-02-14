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
    pass

    # def test_simple_subscribe_gets_message(self):
    #     """
    #     Simple test for setting up a websocket connection
    #     """
    #
    #     set_bootstrap_response({
    #         "allowed_rooms": [{
    #             "target": "message",
    #             "customer": "1"
    #         }]
    #     })
    #
    #     async def run():
    #         async with websockets.connect(WS_URI) as ws:
    #             # allowed rooms
    #             res = await ws.recv()
    #
    #             await ws.send(json.dumps({
    #                 "type": "subscribe",
    #                 "room": {
    #                     "target": "message",
    #                     "customer": "1"
    #                 }
    #             }))
    #
    #             data = {
    #                 "foo": "bar"
    #             }
    #
    #             send_trigger({
    #                 "rooms": [
    #                     {
    #                         "target": "message",
    #                         "customer": "1"
    #                     }
    #
    #                 ],
    #                 "data": data
    #             })
    #
    #             res = await ws.recv()
    #
    #             self.assertEquals(data, json.loads(res))
    #
    #     asyncio.get_event_loop().run_until_complete(run())
