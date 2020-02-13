from aiohttp_requests import requests

from .interface import NoBackendConnectionException, BackendAdapter, Authentication


class BinderAdapter(BackendAdapter):
    '''
    Translates incoming requests from the django app to hub actions
    and vice versa.
    '''

    def __init__(self, app):
        self.app = app
        self.base_url = app.config['API_URL']

    async def get_authentication(self, headers) -> Authentication:
        response = await requests.get('{}bootstrap/'.format(self.base_url))
        if response.status != 200:
            raise NoBackendConnectionException()

        content = await response.json()

        self.app.logger.debug("Binder: Proxy bootstrap. Response: {}".format(content))

        return Authentication(allowed_rooms=content.get('allowed_rooms', []))
