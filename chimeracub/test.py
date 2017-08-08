from collections import deque
from unittest import mock, TestCase as Case
from .hub import Hub
import requests


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


class MockWebSocket:
    closed = False

    def __init__(self):
        self.environ = mock_environ()
        self.incoming_messages = deque()
        self.outgoing_messages = []

    def send(self, message):
        # TODO: maybe test it accepts the same as the OG
        self.outgoing_messages.append(message)

    def close(self):
        self.closed = True

    def mock_incoming_message(self, msg):
        self.incoming_messages.append(msg)

    # Make it selfclosing
    # A blocking test receiver doesn't test well
    def receive(self):
        if not len(self.incoming_messages):
            self.close()
            return

        return self.incoming_messages.popleft()


class MockResponse:
    def __init__(self, json_data={}, status_code=200):
        self.json_data = json_data
        self.status_code = status_code

    def json(self):
        return self.json_data


def mock_api(url, **kwargs):
    return MockResponse({
            'user': {
                'id': 1,
            },
            'allowed_rooms': ['{"target": "ride"}'],
        }, 200)


class Client:
    def __init__(self, app):
        self.app = app
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
        return ws

    def set_mock_api(self, func):
        self._api_mock.side_effect = func

    def _mock_outgoing_requests(self):
        self._api_mock = mock.MagicMock(side_effect=mock_api)
        self._outgoing_requests = mock.patch.object(requests, 'get', self._api_mock)
        self._outgoing_requests.start()
