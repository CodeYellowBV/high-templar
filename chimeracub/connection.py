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

    def send(self, message):
        self.ws.send(json.dumps(message))

    # def subscribe(self, requestId, target, scope=None):
    #     s = Subscription(self, requestId, target, scope)
    #     self.subs.append(s)

    # def unsubscribe(self, requestId):
    #     s = None
    #     for sub in self.subs:
    #         if sub.reqId == requestId:
    #             s = sub

    #     if not s:
    #         return False

    #     self.subs.remove(s)
    #     return True

    # def handle_event(self, target, _type, item, snapshot):
    #     if self.ws.closed:
    #         self.hub.remove(self)
    #         return

    #     for sub in self.subs:
    #         sub.handle_event(target, _type, item, snapshot)

    # def handle(self, db, message):
    #     controller = SocketController(db, self, message)
    #     res = controller.handle()

    #     if type(res) is dict and res['code'] == 'success':
    #         # Handle publish for successful saves, deletes and updates
    #         if res['type'] in ['save', 'update', 'delete']:
    #             self.hub.handle_event(res['target'], res['type'], res['data'], res.get('snapshot', None))

    #     self.ws.send(json.dumps(res))
