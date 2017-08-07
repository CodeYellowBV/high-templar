import uuid


class SocketHandler():
    authenticated = None
    hub = None
    ws = None

    def __init__(self, hub, ws):
        self.uuid = uuid.uuid4()
        self.hub = hub
        self.subs = []
        self.ws = ws

    # def check_auth(self, req):
        

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
