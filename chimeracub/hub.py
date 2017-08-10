import requests
from .connection import Connection


class Adapter:
    '''
    Translates incoming requests from the django app to hub actions
    and vice versa.
    '''

    def __init__(self, app):
        self.app = app
        self.base_url = 'http://{}:{}'.format(app.config['DJANGO_APP_URL'], app.config['DJANGO_APP_PORT'])

    def check_auth(self, socket):
        ws = socket.ws
        headers = {
            'cookie': ws.environ['HTTP_COOKIE'],
            'host': ws.environ['HTTP_HOST'],
            'user-agent': ws.environ['HTTP_USER_AGENT']
        }
        res = requests.get('{}/api/bootstrap/'.format(self.base_url), headers=headers)

        if res.status_code != 200:
            return False

        socket.handle_auth_success(res.json())
        return True


class Hub:
    '''
    Class which manages all connections.
    '''

    def __init__(self, app):
        self.app = app
        self.connections = []
        self.adapter = Adapter(app)

    # def handle_event(self, target, _type, item, snapshot):
    #     # Clone self.connections because they may be removed when closed
    #     for socket in list(self.connections):
    #         socket.handle_event(target, _type, item, snapshot)

    def add_if_auth(self, ws):
        connection = Connection(self, ws)

        auth = self.adapter.check_auth(connection)
        if not auth:
            return False

        self.connections.append(connection)
        return connection

    def add_to_room(self, details, room_name):
        room = self.get_or_create_room(room_name)

    def get_or_create_room(self, room_name):
        return 'bla'
