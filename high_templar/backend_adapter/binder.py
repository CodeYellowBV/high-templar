# from aiohttp_requests import requests
from aiohttp import ClientSession
from .interface import NoBackendConnectionException, BackendAdapter, UnparsableBackendPermissionsException
from high_templar.authentication import Authentication, Permission
from . import header

DEFAULT_HEADERS = {
    'cookie': header.Key('HTTP_COOKIE'),
    'user-agent': header.Key('HTTP_USER_AGENT'),
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
        self.header_definition = {**DEFAULT_HEADERS, **app.config.get('CONNECTION_HEADERS')}

    async def get_authentication(self, headers) -> Authentication:

        for key, value in self.header_definition.items():
            try:
                value = value.get_value(headers)
            except header.NoValue:
                pass
            else:
                self.headers[key] = value

        response = await self.get('bootstrap/'.format(self.base_url))
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

    async def _request(self, method, url, *args, **kwargs):
        url = self.base_url + url
        return await super()._request(method, url, *args, **kwargs)
