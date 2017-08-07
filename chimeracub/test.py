from unittest import mock
# from geventwebsockets import WebSocket, Stream
# from geventwebsockets.handler import WebSocketHandler


class Client:
    def __init__(self, app):
        self.app = app
        self._mock_outgoing_requests()

    def __del__(self):
        print('Test Client: stopping outgoing request mock')
        self._outgoing_requests.stop()

    def open_websocket(self, url='/ws/'):
        # We need to invoke a websocket route with the given url
        # No idea why we can't match on just the url_map
        # So we bind it to an empty context.
        context = self.app.wsgi_app.ws.url_map.bind('')

        # Don't really know what the second part in the matched result tuple is
        route = context.match(url)[0]

        return

        # TODO: create a mock WebSocket
        # gevent-websocket is hard to hack
        # wsh = WebSocketHandler()
        # ws = WebSocket(self.environ, Stream(ws_handler), ws_handler)

    def _mock_outgoing_requests(self):
        self._outgoing_requests = mock.patch('requests.get')
        self._outgoing_requests.start()
