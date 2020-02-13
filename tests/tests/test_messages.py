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
            "allowed_rooms": ["foo"]
        })

        async def run():
            async with websockets.connect(WS_URI) as ws:
                # allowed rooms
                res = await ws.recv()

                send_trigger({
                    "rooms": ["foo"],
                    "data": {
                        "foo": "bar"
                    }
                })
