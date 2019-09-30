import uuid
import json
import threading

from .room import Room

from requests import Session
from werkzeug.http import parse_cookie
from geventwebsocket.exceptions import WebSocketError


class Api(Session):

    def __init__(self, connection):
        super().__init__()

        self.URL_FORMAT = '{}{{}}'.format(connection.hub.adapter.base_url)

        self.headers['cookie'] = connection.ws.environ['HTTP_COOKIE']
        self.headers['host'] = connection.ws.environ['HTTP_HOST']
        self.headers['user-agent'] = connection.ws.environ['HTTP_USER_AGENT']
        FORWARD_IP = connection.hub.app.config.get('FORWARD_IP')
        if FORWARD_IP and FORWARD_IP in connection.ws.environ:
            self.headers['x-forwarded-for'] = connection.ws.environ[FORWARD_IP]

        cookie = parse_cookie(self.headers['cookie'])
        if 'csrftoken' in cookie:
            self.headers['x-csrftoken'] = cookie['csrftoken']

        wz_r = connection.ws.environ.get('werkzeug.request', None)
        if wz_r and 'token' in wz_r.args:
            self.headers['authorization'] = (
                'Token {}'.format(wz_r.args['token'])
            )

    def request(self, method, url, *args, **kwargs):
        url = self.URL_FORMAT.format(url)
        return super().request(method, url, *args, **kwargs)


class Connection():
    ws = None
    hub = None
    user_id = None

    def __init__(self, hub, ws):
        self.ws = ws
        self.hub = hub
        self.subscriptions = {}
        self.allowed_rooms = []
        self.uuid = uuid.uuid4()

        # Nasty hack
        try:
            ws.connection = self
        except AttributeError:
            pass

        self.api = Api(self)

    def get_write_lock(self):
        if not hasattr(self, '_write_lock'):
            self._write_lock = threading.Lock()
        return self._write_lock


    def handle_auth_success(self, data):
        self.user_id = data
        for key in self.hub.app.config.get('USER_ID_PATH', ['user', 'id']):
            try:
                self.user_id = self.user_id[key]
            except (TypeError, KeyError, IndexError):
                self.user_id = None
                break

        self.allowed_rooms = data.get('allowed_rooms', [])

        self.send({'allowed_rooms': self.allowed_rooms})

    def handle(self, message):
        if message == 'ping':
            self.send_raw('pong')
            return

        m = json.loads(message)

        requestId = m.get('requestId', None)

        if m['type'] == 'subscribe':
            return self.handle_subscribe(m)

        if m['type'] == 'unsubscribe':
            return self.handle_unsubscribe(m)

        self.send({
            'requestId': requestId,
            'code': 'error',
            'message': 'message-type-not-allowed',
        })


    # Check that the requested room's keys match any of the allowed rooms,
    def is_room_allowed(self, requested_room_dict):
        def room_matches(ar):
            if len(requested_room_dict.keys()) != len(ar.keys()):
                return False
            for allowed_key, allowed_value in ar.items():
                if allowed_key not in requested_room_dict:
                    return False
                if allowed_value == '*':
                    continue
                if requested_room_dict[allowed_key] != allowed_value:
                    return False

            return True

        for ar in self.allowed_rooms:
            if room_matches(ar):
                return True

        return False


    def handle_subscribe(self, m):
        room_dict = m.get('room', None)
        room_hash = Room.hash_dict(room_dict)

        if not self.is_room_allowed(room_dict):
            self.send({
                'requestId': m['requestId'],
                'code': 'error',
                'message': 'room-not-found',
            })
            return

        sub = self.hub.subscribe(self, m, room_hash)
        self.subscriptions[m['requestId']] = sub
        self.send({
            'requestId': m['requestId'],
            'code': 'success',
        })

    def handle_unsubscribe(self, m):
        reqId = m['requestId']
        if reqId not in self.subscriptions:
            self.send({
                'requestId': m['requestId'],
                'code': 'error',
                'message': 'not-subscribed',
            })
            return

        sub = self.subscriptions[reqId]
        sub.stop()

        self.subscriptions.pop(reqId)
        self.send({
            'requestId': reqId,
            'code': 'success',
        })

    def unsubscribe_all(self):
        for room in [sub.room for sub in self.subscriptions.values()]:
            room.remove_connection(self)

        self.subscriptions = {}

    def send_raw(self, message):
        if self.ws.closed:
            return
        with self.get_write_lock():
            try:
                self.ws.send(message)
            except WebSocketError:
                pass

    def send(self, message):
        self.send_raw(json.dumps(message))
