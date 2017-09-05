import uuid
import json
from .room import Room


class Connection():
    ws = None
    hub = None
    user_id = None

    def __init__(self, hub, ws):
        self.ws = ws
        self.hub = hub
        self.rooms = []
        self.allowed_rooms = []
        self.uuid = uuid.uuid4()

        # Nasty hack
        try:
            ws.connection = self
        except AttributeError:
            pass

    def parse_user(self, user_data):
        self.user_id = user_data['id']

    def handle_auth_success(self, data):
        self.user_id = data['user']['id']
        self.allowed_rooms = data['allowed_rooms']

        self.send({'allowed_rooms': [Room.hash_dict(r) for r in self.allowed_rooms]})

    def handle(self, message):
        if message == 'ping':
            self.ws.send('pong')
            return

        m = json.loads(message)

        requestId = m.get('requestId', None)

        if m['type'] not in ['subscribe']:
            self.send({
                'requestId': requestId,
                'code': 'error',
                'message': 'message-type-not-allowed',
            })

        return self.handle_subscribe(m)

    def is_room_allowed(self, room_hash):
        return room_hash in [Room.hash_dict(ar) for ar in self.allowed_rooms]

    def handle_subscribe(self, m):
        room_dict = m.get('room', None)
        room_hash = Room.hash_dict(room_dict)

        if not self.is_room_allowed(room_hash):
            self.send({
                'requestId': m['requestId'],
                'code': 'error',
                'message': 'room-not-found',
            })

        room = self.hub.add_to_room(self, m, room_hash)
        self.rooms.append(room)
        self.send({
            'requestId': m['requestId'],
            'code': 'success',
        })

    def unsubscribe_all(self):
        for room in self.rooms:
            room.remove_connection(self)

    def send(self, message):
        if self.ws.closed:
            return

        self.ws.send(json.dumps(message))
