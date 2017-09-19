import json
from .testapp.app import app
from high_templar.test import TestCase, Client, MockWebSocket, room_ride, room_car
from greenlet import greenlet

subscribe_ride = {
    'requestId': 'a',
    'type': 'subscribe',
    'room': room_ride,
}
subscribe_car = {
    'requestId': 'b',
    'type': 'subscribe',
    'room': room_car,
}


class TestRoom(TestCase):
    def setUp(self):
        self.client = Client(app)

    def test_subcribe_creates_new(self):
        ws = MockWebSocket()
        ws.mock_incoming_message(json.dumps(subscribe_ride))

        hub = self.client.app.hub

        self.assertEqual(0, len(hub.rooms.keys()))

        g1 = greenlet(self.client.open_connection)
        g1.switch(ws)

        self.assertHubRoomsEqual([room_ride])

        # Test that a room get a reference to its connections
        # and vice versa

        room = self.getHubRoomByDict(room_ride)
        connection = room.connections[0]

        self.assertEqual(ws, connection.ws)
        self.assertEqual([room], [s.room for s in connection.subscriptions.values()])

    def test_subscribe_joins_existing(self):
        ws1 = MockWebSocket()
        ws1.mock_incoming_message(json.dumps(subscribe_ride))
        ws2 = MockWebSocket()
        ws2.mock_incoming_message(json.dumps(subscribe_ride))

        g1 = greenlet(self.client.open_connection)
        g1.switch(ws1)

        self.assertHubRoomsEqual([room_ride])

        room = self.getHubRoomByDict(room_ride)
        c1 = room.connections[0]

        g2 = greenlet(self.client.open_connection)
        g2.switch(ws2)
        self.assertHubRoomsEqual([room_ride])

        c2 = room.connections[1]
        self.assertEqual([c1, c2], room.connections)
        self.assertEqual([room], [s.room for s in c1.subscriptions.values()])
        self.assertEqual([room], [s.room for s in c2.subscriptions.values()])

    def test_close_empty_room(self):
        ws = MockWebSocket()
        ws.mock_incoming_message(json.dumps(subscribe_ride))

        hub = self.client.app.hub

        g1 = greenlet(self.client.open_connection)
        g1.switch(ws)

        self.assertHubRoomsEqual([room_ride])

        ws.connection.unsubscribe_all()
        self.assertEqual(0, len(hub.rooms.keys()))

    def test_keeps_open_nonempty_room(self):
        ws1 = MockWebSocket()
        ws1.mock_incoming_message(json.dumps(subscribe_ride))
        ws2 = MockWebSocket()
        ws2.mock_incoming_message(json.dumps(subscribe_ride))
        ws2.mock_incoming_message(json.dumps(subscribe_car))

        g1 = greenlet(self.client.open_connection)
        g1.switch(ws1)
        g2 = greenlet(self.client.open_connection)
        g2.switch(ws2)

        # Test that both rooms are created and contain
        # the correct connections
        self.assertHubRoomsEqual([room_ride, room_car])
        r_car = self.getHubRoomByDict(room_car)
        self.assertEqual([ws2.connection], r_car.connections)
        r_ride = self.getHubRoomByDict(room_ride)
        self.assertSetEqual(set([ws1.connection, ws2.connection]), set(r_ride.connections))

        # Close the second websocket, unsubscribing if for all the rooms
        ws2.close()

        # Test that the now empty room_car is closed
        self.assertHubRoomsEqual([room_ride])

        # And test that the room_ride still contains ws1
        self.assertEqual([ws1.connection], r_ride.connections)
