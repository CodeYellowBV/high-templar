import uuid
import json
from .room import Room
import requests


class Api:

    def __init__(self, connection):
        self.URL_FORMAT = '{}{{}}'.format(connection.hub.adapter.base_url)

        self.BASE_HEADERS = {
            'cookie': connection.ws.environ['HTTP_COOKIE'],
            'host': connection.ws.environ['HTTP_HOST'],
            'user-agent': connection.ws.environ['HTTP_USER_AGENT']
        }
        wz_r = connection.ws.environ.get('werkzeug.request', None)
        if wz_r and 'token' in wz_r.args:
            self.BASE_HEADERS['Authorization'] = (
                'Token {}'.format(wz_r.args['token'])
            )

    def request(self, method, url, *args, **kwargs):
        url = self.URL_FORMAT.format(url)

        kwargs.setdefault('headers', {})
        for key, value in self.BASE_HEADERS.items():
            kwargs['headers'].setdefault(key, value)

        return getattr(requests, method)(url, *args, **kwargs)

    def get(self, *args, **kwargs):
        return self.request('get', *args, **kwargs)

    def options(self, *args, **kwargs):
        return self.request('options', *args, **kwargs)

    def head(self, *args, **kwargs):
        return self.request('head', *args, **kwargs)

    def post(self, *args, **kwargs):
        return self.request('post', *args, **kwargs)

    def put(self, *args, **kwargs):
        return self.request('put', *args, **kwargs)

    def patch(self, *args, **kwargs):
        return self.request('patch', *args, **kwargs)

    def delete(self, *args, **kwargs):
        return self.request('delete', *args, **kwargs)


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

    def handle_auth_success(self, data):
        user = data.get('user') or {}
        self.user_id = user.get('id')
        self.allowed_rooms = data.get('allowed_rooms', [])

        self.send({'allowed_rooms': self.allowed_rooms})

    def handle(self, message):
        if message == 'ping':
            self.ws.send('pong')
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

    # If all keys match for a certain room,
    def is_room_allowed(self, room_dict):
        def room_matches(rd, ar):
            if len(rd.keys()) != len(ar.keys()):
                return False
            for ar_key in ar.keys():
                if ar_key not in rd:
                    return False
                if ar[ar_key] == '*':
                    continue
                if rd[ar_key] != ar[ar_key]:
                    return False

            return True

        for ar in self.allowed_rooms:
            if room_matches(room_dict, ar):
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

    def send(self, message):
        if self.ws.closed:
            return

        self.ws.send(json.dumps(message))
