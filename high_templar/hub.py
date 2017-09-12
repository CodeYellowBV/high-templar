import requests
from flask import make_response
from .room import Room
from .connection import Connection


class Adapter:
    '''
    Translates incoming requests from the django app to hub actions
    and vice versa.
    '''

    def __init__(self, app):
        self.app = app
        self.base_url = app.config['API_URL']

    def check_auth(self, socket):
        ws = socket.ws

        headers = {
            'cookie': ws.environ['HTTP_COOKIE'],
            'host': ws.environ['HTTP_HOST'],
            'user-agent': ws.environ['HTTP_USER_AGENT']
        }

        wz_r = ws.environ.get('werkzeug.request', None)
        if wz_r and 'token' in wz_r.args:
            headers['Authorization'] = 'Token {}'.format(wz_r.args['token'])

        res = requests.get('{}bootstrap/'.format(self.base_url), headers=headers)

        if res.status_code != 200:
            return False

        socket.handle_auth_success(res.json())
        return True


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
        for room_dict in body['rooms']:
            room_hash = Room.hash_dict(room_dict)
            if room_hash not in self.rooms:
                continue
            connections = self.rooms[room_hash].publish(body['data'])
            closed_connections.extend(connections)

        for r_name, room in self.rooms.copy().items():
            for c in closed_connections:
                c.unsubscribe_all()

        return make_response('publish success')

    def add_if_auth(self, ws):
        connection = Connection(self, ws)

        auth = self.adapter.check_auth(connection)
        if not auth:
            ws.close()
            return False

        return connection

    def get_or_create_room(self, room_hash):
        if room_hash in self.rooms:
            return self.rooms[room_hash]

        room = Room(room_hash, self)
        self.rooms[room_hash] = room
        return room

    def subscribe(self, connection, request, room_hash):
        room = self.get_or_create_room(room_hash)
        sub = room.subscribe(connection, request)
        return sub

    def close_room(self, room):
        # Clone self.rooms because they may be removed when closed
        rooms = self.rooms.copy()
        for r_name, r in rooms.items():
            if r == room:
                del self.rooms[r_name]
