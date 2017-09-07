import json
from .testapp.app import app
from high_templar.test import TestCase, Client, MockWebSocket, room_car
from greenlet import greenlet

subscribe_car = {
    'requestId': 'car',
    'type': 'subscribe',
    'room': room_car,
}

unsubscribe_car = {
    'requestId': 'car',
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

    # test doesnt receive messages
    #
    # test room closes if empty
    #
    # test subscription removed from connection
    #
    # test cannot unsubscribe from non subscription

