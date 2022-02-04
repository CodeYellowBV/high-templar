from aiohttp import ClientSession
from high_templar.backend_adapter import BinderAdapter
from high_templar.backend_adapter.interface import BackendAdapter
from high_templar.main import create_app
from settings import WS_URI
from unittest import TestCase
from unittest.mock import patch
from .utils.wiremock import set_bootstrap_response
import asyncio


class TestAdapter(TestCase):
    """
    Tests for the backend adapters
    """

    def test_request_kwargs_config(self):
        """
        Test that the REQUEST_KWARGS in app.config are sent along with
        each request
        """

        async def run():
            with patch.object(ClientSession, '_request', return_value=asyncio.sleep(0.1)) as mock_method:
                class Settings():
                    API_URL = ''
                    REQUEST_KWARGS = {'test1234': 'test1234'}

                app = create_app(Settings())
                adapter = BinderAdapter(app)
                await adapter._request('GET', '')
            mock_method.assert_called_once_with('GET', '', headers={}, test1234='test1234')
        asyncio.get_event_loop().run_until_complete(run())

    def test_session_kwargs_config(self):
        """
        Test that BinderAdapter propagates the SESSION_KWARGS in 
        app.config to the ClientSession constructor
        """

        with patch.object(ClientSession, '__init__', return_value=None) as mock_method:
            class Settings():
                API_URL = ''
                SESSION_KWARGS = {'test123': 123}
            
            app = create_app(Settings())
            BinderAdapter(app)

        mock_method.assert_called_once_with(test123=123)
