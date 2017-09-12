import requests
import json
from .testapp.app import app, api_url
from high_templar.test import TestCase, Client, MockResponse, MockWebSocket, room_ride, room_car


class TestAuth(TestCase):
    def setUp(self):
        self.client = Client(app)

    def test_incoming_websocket_calls_bootstrap(self):
        ws = MockWebSocket()
        self.client.open_connection(ws)
        self.assertEqual(1, requests.get.call_count)

        external_url = '{}bootstrap/'.format(api_url)
        self.assertEqual(external_url, requests.get.call_args_list[0][0][0])

    def test_token_query_param_to_auth_header(self):
        class WerkzeugRequest:
            def __init__(self, token):
                self.token = token

            @property
            def args(self):
                return {'token': self.token}

        ws = MockWebSocket()
        ws.environ['werkzeug.request'] = WerkzeugRequest('itsmeyourelookingfor')
        self.client.open_connection(ws)
        self.assertEqual(1, requests.get.call_count)
        self.assertTrue('Authorization' in requests.get.call_args_list[0][1]['headers'])
        self.assertEqual('Token itsmeyourelookingfor', requests.get.call_args_list[0][1]['headers']['Authorization'])

    def test_unauth_closed(self):
        def not_authenticated(request, **kwargs):
            return MockResponse({}, 403)

        self.client.set_mock_api(not_authenticated)

        ws = MockWebSocket()
        self.client.open_connection(ws)

        self.assertEqual(True, ws.closed)

    def test_lists_allowed_rooms(self):
        ws = MockWebSocket()
        self.client.open_connection(ws)

        res = json.loads(ws.outgoing_messages[0])
        self.assertCountEqual([room_ride, room_car], res['allowed_rooms'])
