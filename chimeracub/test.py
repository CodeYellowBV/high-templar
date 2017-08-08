from unittest import mock
# from geventwebsockets import WebSocket, Stream
# from geventwebsockets.handler import WebSocketHandler


def mock_environ():
    return {
        'HTTP_COOKIE': 'sessionid=foo; csrftoken=bar',
        'HTTP_HOST': 'webapp.test',
        'HTTP_USER_AGENT': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36',
    }


class MockWebSocket:
    closed = False

    def __init__(self):
        self.environ = mock_environ()
        self.sent_messages = []

    def send(self, message):
        # TODO: maybe test it accepts the same as the OG
        self.sent_messages.append(message)

    def close(self):
        self.closed = True


class Client:
    def __init__(self, app):
        self.app = app
        self._mock_outgoing_requests()

    def __del__(self):
        self._outgoing_requests.stop()

    def open_websocket(self, url='/ws/'):
        # We need to invoke a websocket route with the given url
        # No idea why we can't match on just the url_map
        # So we bind it to an empty context.
        context = self.app.wsgi_app.ws.url_map.bind('')

        # Don't really know what the second part in the matched result tuple is
        route = context.match(url)[0]

        ws = MockWebSocket()
        route(ws)

    def _mock_outgoing_requests(self):
        self._outgoing_requests = mock.patch('requests.get')
        self._outgoing_requests.start()
