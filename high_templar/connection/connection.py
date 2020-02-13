import uuid
import json
import threading
from time import sleep

import gevent
from requests import Session

from room import Room
from . import header

DEFAULT_HEADERS = {
    'cookie': header.Key('HTTP_COOKIE'),
    'host': header.Key('HTTP_HOST'),
    'user-agent': header.Key('HTTP_USER_AGENT'),
    'x-csrftoken': header.Cookie('csrftoken'),
    'authorization': header.Param('token').map('Token {}'.format),
}


class Api(Session):

    def __init__(self, app, connection):
        super().__init__()

        self.app = app

        self.URL_FORMAT = '{}{{}}'.format(connection.hub.adapter.base_url)

        FORWARD_IP = connection.hub.app.config.get('FORWARD_IP')
        if FORWARD_IP and FORWARD_IP in connection.ws.environ:
            self.headers['x-forwarded-for'] = connection.ws.environ[FORWARD_IP]

        headers = connection.hub.app.config.get('CONNECTION_HEADERS')
        if headers:
            headers = {**DEFAULT_HEADERS, **headers}
        else:
            headers = DEFAULT_HEADERS

        for key, value in headers.items():
            try:
                value = value.get_value(connection.ws.environ)
            except header.NoValue:
                pass
            except Exception as e:
                self.app.logger.error(e)
                raise e
            else:
                self.headers[key] = value

    def request(self, method, url, *args, **kwargs):
        url = self.URL_FORMAT.format(url)
        return super().request(method, url, *args, **kwargs)


class Connection():
    ws = None
    hub = None
    user_id = None

    def __init__(self, hub, ws, app):
        self.ws = ws
        self.hub = hub
        self.subscriptions = {}
        self.allowed_rooms = []
        self.uuid = uuid.uuid4()
        self.app = app

        # Nasty hack
        try:
            ws.connection = self
        except AttributeError:
            pass

        self.api = Api(self.app, self)

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

        self.send({'is_authorized': True, 'allowed_rooms': self.allowed_rooms})

    def handle_auth_not_success(self):
        """
        This is called when we can not authenticate ourselves successfully at the binder backend. If this is the
        case, we send a message with is_authorized = False, and close the connection, such that frontend
        knows what to do

        :return:
        """

        # Send a notification that the connection is not authorized. This is mainly meant for debugging why a
        # connection is not set up.
        self.send({'is_authorized': False})
        self.app.logger.debug("Closing connection because can't authorize the user")

        # Make the thread sleep for a bit, to make sure the other end can read the message.
        sleep(0.1)
        self.ws.close()

    def handle(self, message):
        if message == 'ping':
            self.send_raw('pong')
            for hook in self.hub.ping_hooks:
                hook(self)
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

        def _send(ws, message):
            ws.stream.handler.socket.settimeout(0.1)
            ws.send(message)
            ws.stream.handler.socket.settimeout(None)

        gevent.spawn(_send, self.ws, message)

    def send(self, message):
        self.send_raw(json.dumps(message))
