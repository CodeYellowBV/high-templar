import unittest
import requests
from testapp.app import app, django_app_url, django_app_port
from chimeracub.test import Client


class TestAuth(unittest.TestCase):
    def setUp(self):
        self.client = Client(app)

    def test_incoming_websocket_calls_bootstrap(self):
        self.client.open_websocket()
        self.assertEqual(1, requests.get.call_count)

        external_url = '{}:{}/api/bootstrap'.format(django_app_url, django_app_port)
        self.assertEqual(external_url, requests.get.call_args_list[0][0])
