from .testapp.app import app
from high_templar.test import TestCase, Client, MockWebSocket


class TestKeepalive(TestCase):
    def setUp(self):
        self.client = Client(app)

    def test_ping_pong(self):
        ws = MockWebSocket()
        ws.mock_incoming_message('ping')
        self.client.open_connection(ws)

        self.assertEqual(2, len(ws.outgoing_messages))
        self.assertEqual('pong', ws.outgoing_messages[1])
