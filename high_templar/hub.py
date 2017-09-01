import json
import requests
from flask import make_response
from .connection import Connection


class WebSocketClosedError(Exception):
    pass


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
    "exist" between quotation marks, because high-templar only creates a room when someone actually subscribes to it.

    A room keeps track of all connections with the same scoped permission.
    In the case a view_action.own, it would have a maximum of 1 connection.
    '''

    def __init__(self, name, hub):
        self.name = name
        self.hub = hub
        self.subscriptions = []

    def subscribe(self, connection, request):
        sub = Subscription(connection, request)
        self.subscriptions.append(sub)

    # Don't just unsubscribe: remove all subscriptions for a connection
    def remove_connection(self, connection):
        # Clone self.subscriptions because they may be removed when closed
        for s in list(self.subscriptions):
            if s.connection == connection:
                self.subscriptions.remove(s)

        self.close_if_empty()

    def close_if_empty(self):
        if not self.subscriptions:
            self.close()

    def close(self):
        self.hub.close_room(self)

    # Returns a list of closed connections
    def publish(self, data):
        closed_connections = []
        for s in self.subscriptions:
            try:
                s.publish(data)
            except WebSocketClosedError:
                closed_connections.append(s.connection)

        return closed_connections

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

    def publish(self, data):
        if self.connection.ws.closed:
            raise WebSocketClosedError

        self.connection.ws.send(json.dumps({
            'requestId': self.requestId,
            'type': 'publish',
            'data': data,
        }))


class Hub:
    '''
    Manages all connections.
    '''

    def __init__(self, app):
        self.app = app
        self.rooms = {}
        self.adapter = Adapter(app)

    def handle_trigger(self, body):
        if 'rooms' not in body:
            return make_response('rooms not specified', 400)
        if 'data' not in body:
            return make_response('data not specified', 400)

        closed_connections = []
        for r in body['rooms']:
            if r not in self.rooms:
                continue
            connections = self.rooms[r].publish(body['data'])
            closed_connections.extend(connections)

        for r_name, room in self.rooms.copy().items():
            for c in closed_connections:
                room.remove_connection(c)

        return make_response('publish success')

    def add_if_auth(self, ws):
        connection = Connection(self, ws)

        auth = self.adapter.check_auth(connection)
        if not auth:
            ws.close()
            return False

        return connection

    def get_or_create_room(self, room_name):
        if room_name in self.rooms:
            return self.rooms[room_name]

        room = Room(room_name, self)
        self.rooms[room_name] = room
        return room

    def add_to_room(self, connection, request, room_name):
        room = self.get_or_create_room(room_name)
        room.subscribe(connection, request)
        return room

    def close_room(self, room):
        # Clone self.rooms because they may be removed when closed
        rooms = self.rooms.copy()
        for r_name, r in rooms.items():
            if r == room:
                del self.rooms[r_name]
