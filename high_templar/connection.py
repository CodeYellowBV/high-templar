import uuid
import json


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

        # Rooms are serialized JSON
        # We don't want to double serialize it
        rooms = [json.loads(r) for r in self.allowed_rooms]
        self.send({'allowed_rooms': rooms})

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

    def handle_subscribe(self, m):
        room = m.get('room', None)
        if room not in self.allowed_rooms:
            self.send({
                'requestId': m['requestId'],
                'code': 'error',
                'message': 'room-not-found',
            })

        room = self.hub.add_to_room(self, m, room)
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
