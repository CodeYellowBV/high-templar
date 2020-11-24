# from aiohttp_requests import requests
from aiohttp import ClientSession
from .interface import NoBackendConnectionException, BackendAdapter, UnparsableBackendPermissionsException
from high_templar.authentication import Authentication, Permission
from . import header
from werkzeug.datastructures import Headers

DEFAULT_HEADERS = {
    'cookie': header.Key('Cookie'),
    'user-agent': header.Key('User-Agent'),
    'x-csrftoken': header.Cookie('csrftoken'),
    'authorization': header.Param('token').map('Token {}'.format),
}


class BinderAdapter(BackendAdapter, ClientSession):
    '''
    Translates incoming requests from the django app to hub actions
    and vice versa.
    '''

    def __init__(self, app):
        super().__init__()
        self.app = app
        self.base_url = app.config['API_URL']
        self.forward_ip = app.config.get('FORWARD_IP')
        self.header_definition = {**DEFAULT_HEADERS, **app.config.get('CONNECTION_HEADERS', {})}
        self.headers = {}

    async def get_authentication(self, websocket) -> Authentication:

        for key, value in self.header_definition.items():
            try:
                value = value.get_value(websocket)
            except header.NoValue as e:
                self.app.logger.debug('Can\'t find header {} {} {}'.format(key, value, e))
            else:
                self.headers[key] = value

        self.app.logger.debug(websocket.args)
        self.app.logger.debug(websocket.args.get('session_token'))

        response = await self.get('bootstrap/')

        if response.status != 200:
            raise NoBackendConnectionException()

        content = await response.json()

        self.app.logger.debug("Binder: Proxy bootstrap. Response: {}".format(content))

        try:
            return Authentication(allowed_rooms=list(
                map(lambda x: Permission(x), content.get('allowed_rooms', []))
            ))
        except (AttributeError, ValueError):
            self.app.logger.info("Binder: could not understand permissions {}".format(content.get('allowed_rooms')))
            raise UnparsableBackendPermissionsException()

    async def _request(self, method, url, *, headers={}, **kwargs):
        url = self.base_url + url
        headers = {**self.headers, **headers}
        return await super()._request(method, url, headers=headers,  **kwargs)
