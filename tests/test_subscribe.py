import json
from .testapp.app import app
from high_templar.test import TestCase, Client, MockWebSocket, room_ride, room_car

subscribe_ride = {
    'requestId': 'a',
    'type': 'subscribe',
    'room': room_ride,
}
subscribe_weird = {
    'requestId': 'b',
    'type': 'subscribe',
    'room': 'weird',
}


class TestSubscribe(TestCase):
    def setUp(self):
        self.client = Client(app)

    def test_subscribe_success(self):
        ws = MockWebSocket()
        ws.mock_incoming_message(json.dumps(subscribe_ride))
        self.client.open_connection(ws)

        self.assertEqual({'requestId': 'a', 'code': 'success'}, json.loads(ws.outgoing_messages[1]))

    def test_subscribe_unallowed_room(self):
        ws = MockWebSocket()
        ws.mock_incoming_message(json.dumps(subscribe_weird))
        self.client.open_connection(ws)

        self.assertEqual({'requestId': 'b', 'code': 'error', 'message': 'room-not-found'}, json.loads(ws.outgoing_messages[1]))
