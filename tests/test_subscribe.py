import json
from .testapp.app import app
from high_templar.test import TestCase, Client, MockWebSocket, room_car, room_car_reverse, MockResponse

subscribe_car = {
    'requestId': 'a',
    'type': 'subscribe',
    'room': room_car,
}
subscribe_car_reverse = {
    'requestId': 'a',
    'type': 'subscribe',
    'room': room_car_reverse,
}
subscribe_weird = {
    'requestId': 'b',
    'type': 'subscribe',
    'room': {'foo': 'bar'},
}


class TestSubscribe(TestCase):
    def setUp(self):
        self.client = Client(app)

    def test_subscribe_success(self):
        ws = MockWebSocket()
        ws.mock_incoming_message(json.dumps(subscribe_car))
        self.client.open_connection(ws)

        self.assertEqual({'requestId': 'a', 'code': 'success'}, json.loads(ws.outgoing_messages[1]))

    def test_room_key_order_unimportant(self):
        ws = MockWebSocket()
        ws.mock_incoming_message(json.dumps(subscribe_car_reverse))
        self.client.open_connection(ws)

        self.assertEqual({'requestId': 'a', 'code': 'success'}, json.loads(ws.outgoing_messages[1]))

    def test_subscribe_unallowed_room(self):
        ws = MockWebSocket()
        ws.mock_incoming_message(json.dumps(subscribe_weird))
        self.client.open_connection(ws)

        self.assertEqual({'requestId': 'b', 'code': 'error', 'message': 'room-not-found'}, json.loads(ws.outgoing_messages[1]))


class TestAllowedRoomMatch(TestCase):
    def setUp(self):
        self.client = Client(app)

    def test_wildcard(self):
        allowed_car_all = {'target': 'car', 'car': '*'}

        def allowed_car_wildcard(request, **kwargs):
            return MockResponse({
                'user': {'id': 1},
                'allowed_rooms': [allowed_car_all],
            }, 200)

        self.client.set_mock_api(allowed_car_wildcard)

        ws = MockWebSocket()
        ws.mock_incoming_message(json.dumps(subscribe_car))
        self.client.open_connection(ws)

        self.assertEqual({'requestId': 'a', 'code': 'success'}, json.loads(ws.outgoing_messages[1]))

    def test_empty_dict(self):
        def empty_dict_allowed(request, **kwargs):
            return MockResponse({
                'user': {'id': 1},
                'allowed_rooms': [{}],
            }, 200)

        self.client.set_mock_api(empty_dict_allowed)

        ws = MockWebSocket()
        ws.mock_incoming_message(json.dumps(subscribe_car))
        self.client.open_connection(ws)

        self.assertEqual(2, len(ws.outgoing_messages))
        self.assertEqual({'requestId': 'a', 'code': 'error', 'message': 'room-not-found'}, json.loads(ws.outgoing_messages[1]))

    def test_mismatched_key(self):
        def empty_dict_allowed(request, **kwargs):
            return MockResponse({
                'user': {'id': 1},
                'allowed_rooms': [{
                    'target': 'car',
                    'foo': 1,
                }],
            }, 200)

        self.client.set_mock_api(empty_dict_allowed)

        ws = MockWebSocket()
        ws.mock_incoming_message(json.dumps(subscribe_car))
        self.client.open_connection(ws)

        self.assertEqual(2, len(ws.outgoing_messages))
        self.assertEqual({'requestId': 'a', 'code': 'error', 'message': 'room-not-found'}, json.loads(ws.outgoing_messages[1]))
