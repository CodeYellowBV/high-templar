import json
import unittest
from .testapp.app import app
from chimeracub.test import TestCase, Client, MockWebSocket
from greenlet import greenlet

room_ride = json.dumps({'target': 'ride'})
subscribe_ride = {
    'requestId': 'a',
    'type': 'subscribe',
    'room': room_ride,
}
room_car = json.dumps({'target': 'car'})
subscribe_car = {
    'requestId': 'b',
    'type': 'subscribe',
    'room': room_car,
}


class TestRoom(TestCase):
    def setUp(self):
        self.client = Client(app)

    @unittest.skip('TODO: Schedule greenlets in test runner')
    def test_subcribe_creates_new(self):
        ws = MockWebSocket()
        ws.mock_incoming_message(json.dumps(subscribe_ride))

        hub = self.client.app.hub

        self.assertEqual(0, len(hub.rooms.keys()))

        self.client.open_connection(ws)
        self.assertEqual([room_ride], list(hub.rooms.keys()))

        # Test that a room get a reference to its connections
        # and vice versa

        room = hub.rooms[room_ride]
        connection = room.connections[0]

        self.assertEqual(ws, connection.ws)
        self.assertEqual([room], connection.rooms)

    @unittest.skip('TODO: Schedule greenlets in test runner')
    def test_subscribe_joins_existing(self):
        ws1 = MockWebSocket()
        ws1.mock_incoming_message(json.dumps(subscribe_ride))
        ws2 = MockWebSocket()
        ws2.mock_incoming_message(json.dumps(subscribe_ride))

        hub = self.client.app.hub
        self.client.open_connection(ws1)

        self.assertEqual([room_ride], list(hub.rooms.keys()))

        room = hub.rooms[room_ride]
        c1 = room.connections[0]

        self.client.open_connection(ws2)
        self.assertEqual([room_ride], list(hub.rooms.keys()))

        c2 = room.connections[1]
        self.assertEqual([c1, c2], room.connections)
        self.assertEqual([room], c1.rooms)
        self.assertEqual([room], c2.rooms)

    def test_close_empty_room(self):
        ws = MockWebSocket()
        ws.mock_incoming_message(json.dumps(subscribe_ride))

        hub = self.client.app.hub

        g1 = greenlet(self.client.open_connection)
        ws.pending_actions.append(ws.resume_tests)
        g1.switch(ws)

        self.assertEqual([room_ride], list(hub.rooms.keys()))

        ws.connection.unsubscribe_all()
        self.assertEqual(0, len(hub.rooms.keys()))

    # def test_subscribe_success(self):

    #     self.assertEqual({'requestId': 'a', 'code': 'success'}, json.loads(ws.outgoing_messages[1]))

    # def test_subscribe_unallowed_room(self):
    #     ws = MockWebSocket()
    #     ws.mock_incoming_message(json.dumps(subscribe_car))
    #     self.client.open_connection(ws)

        # self.assertEqual({'requestId': 'b', 'code': 'error', 'message': 'room-not-found'}, json.loads(ws.outgoing_messages[1]))
