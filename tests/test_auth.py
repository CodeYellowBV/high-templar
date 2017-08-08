import requests
from .testapp.app import app, django_app_url, django_app_port
from chimeracub.test import TestCase, Client, MockResponse


class TestAuth(TestCase):
    def setUp(self):
        self.client = Client(app)

    def test_incoming_websocket_calls_bootstrap(self):
        self.client.open_websocket()
        self.assertEqual(1, requests.get.call_count)

        external_url = 'http://{}:{}/api/bootstrap/'.format(django_app_url, django_app_port)
        self.assertEqual(external_url, requests.get.call_args_list[0][0][0])

    def test_added_to_hub(self):
        self.client.open_websocket()
        hub = self.client.app.hub

        self.assertEqual(1, len(hub.sockets))

    def test_unauth_not_added_to_hub(self):
        def not_authenticated(request, **kwargs):
            return MockResponse({}, 403)

        self.client.set_mock_api(not_authenticated)
        self.client.open_websocket()
        hub = self.client.app.hub

        self.assertEqual(0, len(hub.sockets))
