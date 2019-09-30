import json
from .testapp.app import app, api_url
from high_templar.test import TestCase, Client, MockResponse, MockWebSocket, room_ride, room_car, room_bicycle_wildcard


class TestAuth(TestCase):
    def test_incoming_websocket_calls_bootstrap(self):
        ws = MockWebSocket()
        self.client.open_connection(ws)
        self.assertEqual(1, self.client.mock_send.call_count)

        external_url = '{}bootstrap/'.format(api_url)
        request = self.client.mock_send.call_args_list[0][0][0]
        self.assertEqual('GET', request.method)
        self.assertEqual(external_url, request.url)

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
        self.assertEqual(1, self.client.mock_send.call_count)
        request = self.client.mock_send.call_args_list[0][0][0]
        self.assertIn('Authorization', request.headers)
        self.assertEqual('Token itsmeyourelookingfor', request.headers['Authorization'])

    def test_ip_forward(self):
        ws = MockWebSocket()
        # Fake nginx IP resolving
        ws.environ['HTTP_X_REAL_IP'] = '1.2.3.4'
        self.client.open_connection(ws)
        self.assertEqual(1, self.client.mock_send.call_count)
        request = self.client.mock_send.call_args_list[0][0][0]
        self.assertIn('X-Forwarded-For', request.headers)
        self.assertEqual('1.2.3.4', request.headers['X-Forwarded-For'])

    def test_ip_forward_not_provided(self):
        ws = MockWebSocket()
        self.client.open_connection(ws)
        self.assertEqual(1, self.client.mock_send.call_count)
        request = self.client.mock_send.call_args_list[0][0][0]
        self.assertNotIn('X-Forwarded-For', request.headers)

    def test_unauth_closed(self):
        @self.client.set_mock_api
        def not_authenticated(request, **kwargs):
            return MockResponse({}, 403)

        ws = MockWebSocket()
        self.client.open_connection(ws)

        self.assertEqual(True, ws.closed)


    def test_auth_but_not_logged_in_closed(self):
        @self.client.set_mock_api
        def not_logged_in(request, **kwargs):
            return MockResponse({'user': None}, 200)

        ws = MockWebSocket()
        self.client.open_connection(ws)

        # We do get a response, but the rooms are simply empty if
        # there's no user object in the response.
        res = json.loads(ws.outgoing_messages[0])
        self.assertCountEqual([], res['allowed_rooms'])

        self.assertEqual(True, ws.closed)


    def test_lists_allowed_rooms(self):
        ws = MockWebSocket()
        self.client.open_connection(ws)

        res = json.loads(ws.outgoing_messages[0])
        self.assertCountEqual([room_ride, room_car, room_bicycle_wildcard], res['allowed_rooms'])
