from collections import deque
from unittest import mock, TestCase as Case
from geventwebsocket.exceptions import WebSocketError
from geventwebsocket.websocket import MSG_ALREADY_CLOSED
from .hub import Hub
from .room import Room
from greenlet import greenlet
import requests
import json


def mock_environ():
    return {
        'HTTP_COOKIE': 'sessionid=foo; csrftoken=bar',
        'HTTP_HOST': 'webapp.test',
        'HTTP_USER_AGENT': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36',
    }


class TestCase(Case):
    # Reset the Hub
    # Otherwise the hub still has the socket of the previous test
    def tearDown(self):
        if self.client:
            self.client.app.hub = Hub(self.client.app)

    # Shorthand for hashing rooms
    # Converting to sets etc.
    def assertHubRoomsEqual(self, room_dicts):
        hub = self.client.app.hub

        room_hashes = [Room.hash_dict(r) for r in room_dicts]
        return self.assertSetEqual(set(room_hashes), set(hub.rooms.keys()))

    def getHubRoomByDict(self, room_dict):
        hub = self.client.app.hub
        room_hash = Room.hash_dict(room_dict)
        return hub.rooms[room_hash]

    def trigger(self, data):
        self.client.flask_test_client.post(
            '/trigger/',
            content_type='application/json',
            data=json.dumps(data))


class MockWebSocket:
    closed = False
    connection = None

    def __init__(self):
        self.environ = mock_environ()
        self.pending_actions = deque()
        self.outgoing_messages = []

    def send(self, message):
        if self.closed:
            raise WebSocketError(MSG_ALREADY_CLOSED)

        self.outgoing_messages.append(message)

    def close(self):
        self.connection.unsubscribe_all()
        self.closed = True

    def mock_incoming_message(self, msg):
        self.pending_actions.append(self.receive_message(msg))

    def resume_tests(self):
        g_self = greenlet.getcurrent()

        # Switch to the main thread if we are using greenlets.
        # Otherwise just close to jump out of the ws.receive loop
        if g_self.parent:
            g_self.parent.switch()
        else:
            self.close()

    def receive_message(self, msg):
        return msg

    def receive(self):
        result = None
        # Concurrency loop
        # This stack can contain a greenlet switch (method)
        # Or a message receive (str)
        while not result:
            if not len(self.pending_actions):
                self.resume_tests()
                return
            next_action = self.pending_actions.popleft()

            if callable(next_action):
                next_action()
            else:
                result = next_action

        return result


class MockResponse:
    def __init__(self, json_data={}, status_code=200):
        self.json_data = json_data
        self.status_code = status_code

    def json(self):
        return self.json_data


room_ride = {'target': 'ride'}
room_car = {'target': 'car', 'car': 1}
room_car_reverse = {'car': 1, 'target': 'car'}


def mock_api(url, **kwargs):
    return MockResponse({
            'user': {
                'id': 1,
            },
            'allowed_rooms': [room_ride, room_car],
        }, 200)


class Client:
    def __init__(self, app):
        self.app = app
        self.app.testing = True
        self.flask_test_client = self.app.test_client()
        self._mock_outgoing_requests()

    def __del__(self):
        self._outgoing_requests.stop()

    def open_connection(self, ws, url='/ws/'):
        # We need to invoke a websocket route with the given url
        # No idea why we can't match on just the url_map
        # So we bind it to an empty context.
        context = self.app.wsgi_app.ws.url_map.bind('')

        # Don't really know what the second part in the matched result tuple is
        route = context.match(url)[0]

        route(ws)

    def set_mock_api(self, func):
        self._api_mock.side_effect = func

    def _mock_outgoing_requests(self):
        self._api_mock = mock.MagicMock(side_effect=mock_api)
        self._outgoing_requests = mock.patch.object(requests, 'get', self._api_mock)
        self._outgoing_requests.start()
