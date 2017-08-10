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


class Room:
    '''
    A collection of subscriptions which have access to a scoped permission.

    A permission would be: See actions
    A scoped permission would be: See your own actions

    Then there would "exist" a room for every single user with view_action.own scoped permission
    "exist" between quotation marks, because chimera only creates a room when someone actually subscribes to it.

    A room keeps track of all connections with the same scoped permission.
    In the case a view_action.own, it would have a maximum of 1 connection.
    '''

    def __init__(self, name):
        self.name = name
        self.subscriptions = []

    def subscribe(self, connection, request):
        sub = Subscription(connection, request)
        self.subscriptions.append(sub)

    @property
    def connections(self):
        return [s.connection for s in self.subscriptions]


class Subscription:
    '''
    A subscription of a connection to a room
    '''

    def __init__(self, connection, request):
        self.connection = connection
        self.requestId = request['requestId']
        self.scope = request.get('scope', {})


class Hub:
    '''
    Manages all connections.
    '''

    def __init__(self, app):
        self.app = app
        self.rooms = {}
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

    def get_or_create_room(self, room_name):
        if room_name in self.rooms:
            return self.rooms[room_name]

        room = Room(room_name)
        self.rooms[room_name] = room
        return room

    def add_to_room(self, connection, request, room_name):
        room = self.get_or_create_room(room_name)
        room.subscribe(connection, request)
        return room
