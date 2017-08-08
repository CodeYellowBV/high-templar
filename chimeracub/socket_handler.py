import uuid
import json


class SocketHandler():
    ws = None
    hub = None
    user_id = None
    allowed_rooms = []
    authenticated = None

    def __init__(self, hub, ws):
        self.uuid = uuid.uuid4()
        self.hub = hub
        self.allowed_rooms = []
        self.ws = ws

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
