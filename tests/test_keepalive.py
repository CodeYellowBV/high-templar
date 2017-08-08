from .testapp.app import app
from chimeracub.test import TestCase, Client, MockWebSocket


class TestKeepalive(TestCase):
    def setUp(self):
        self.client = Client(app)

    def test_ping_pong(self):
        ws = MockWebSocket()
        ws.mock_incoming_message('ping')
        self.client.open_connection(ws)

        self.assertEqual(1, len(ws.outgoing_messages))
        self.assertEqual('pong', ws.outgoing_messages[0])

