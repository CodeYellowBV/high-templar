import unittest
from testapp import app


class TestAuth(unittest.TestCase):
    def setUp(self):
        self.app = app

    def test_incoming_websocket_proxies_bootstrap(self):
        # from pudb import set_trace; set_trace()
        self.assertEqual(False, True)
