import json
from .testapp.app import app
from high_templar.test import TestCase, Client, MockWebSocket, room_car
from greenlet import greenlet

subscribe_car = {
    'requestId': 'car',
    'type': 'subscribe',
    'room': room_car,
}

subscribe_car_2 = {
    'requestId': 'car_2',
    'type': 'subscribe',
    'room': room_car,
}

unsubscribe_car = {
    'requestId': 'car',
    'type': 'unsubscribe',
}

unsubscribe_car_2 = {
    'requestId': 'car_2',
    'type': 'unsubscribe',
}


class TestUnsubscribe(TestCase):
    def setUp(self):
        self.client = Client(app)

    def test_no_more_publish(self):
        ws = MockWebSocket()
        ws.mock_incoming_message(json.dumps(subscribe_car))

        g = greenlet(self.client.open_connection)
        g.switch(ws)

        self.assertEqual(2, len(ws.outgoing_messages))
        self.assertEqual({'requestId': 'car', 'code': 'success'}, json.loads(ws.outgoing_messages[1]))

        self.trigger({
                'rooms': [room_car],
                'data': [{'id': 1}]
            })

        g.switch()
        self.assertEqual(3, len(ws.outgoing_messages))
        self.assertEqual({
            'requestId': 'car',
            'type': 'publish',
            'data': [{'id': 1}]
            }, json.loads(ws.outgoing_messages[2]))

        ws.mock_incoming_message(json.dumps(unsubscribe_car))

        g.switch()
        self.assertEqual(4, len(ws.outgoing_messages))
        self.assertEqual({'requestId': 'car', 'code': 'success'}, json.loads(ws.outgoing_messages[3]))

        self.trigger({
                'rooms': [room_car],
                'data': [{'id': 1}]
            })

        g.switch()
        self.assertEqual(4, len(ws.outgoing_messages))

    def test_sub_removed_from_room(self):
        ws1 = MockWebSocket()
        ws1.mock_incoming_message(json.dumps(subscribe_car))
        ws2 = MockWebSocket()
        ws2.mock_incoming_message(json.dumps(subscribe_car_2))

        g1 = greenlet(self.client.open_connection)
        g1.switch(ws1)
        g2 = greenlet(self.client.open_connection)
        g2.switch(ws2)

        room = self.getHubRoomByDict(room_car)
        c1 = room.connections[0]
        c2 = room.connections[1]

        self.assertHubRoomsEqual([room_car])
        self.assertEqual([c1, c2], room.connections)
        self.assertEqual([room], [s.room for s in c1.subscriptions.values()])
        self.assertEqual([room], [s.room for s in c2.subscriptions.values()])

        ws2.mock_incoming_message(json.dumps(unsubscribe_car_2))
        g2.switch()

        self.assertHubRoomsEqual([room_car])
        self.assertEqual([c1], room.connections)
        self.assertEqual([room], [s.room for s in c1.subscriptions.values()])
        self.assertEqual(0, len(c2.subscriptions))

        ws1.mock_incoming_message(json.dumps(unsubscribe_car))
        g1.switch()

        self.assertHubRoomsEqual([])
        self.assertEqual(0, len(c1.subscriptions))
        self.assertEqual(0, len(c2.subscriptions))

    def test_cannot_unsubscribe_when_not_subscribed(self):
        ws = MockWebSocket()
        ws.mock_incoming_message(json.dumps(unsubscribe_car))

        self.client.open_connection(ws)
        self.assertEqual(2, len(ws.outgoing_messages))
        self.assertEqual({'requestId': 'car', 'code': 'error', 'message': 'not-subscribed'}, json.loads(ws.outgoing_messages[1]))
