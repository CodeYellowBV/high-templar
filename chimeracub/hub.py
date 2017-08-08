from .socket_handler import SocketHandler
from .adapter import Adapter


class Hub():
    '''
    Class which connects all sockets.
    '''

    def __init__(self, app):
        self.app = app
        self.sockets = []
        self.adapter = Adapter(app)

    # def handle_event(self, target, _type, item, snapshot):
    #     # Clone self.sockets because they may be removed when closed
    #     for socket in list(self.sockets):
    #         socket.handle_event(target, _type, item, snapshot)

    def add_if_auth(self, ws):
        socket = SocketHandler(self, ws)

        auth = self.adapter.check_auth(socket)
        if not auth:
            return False

        self.sockets.append(socket)
        return socket

    def add_to_room(self, details, room_name):
        room = self.get_or_create_room(room_name)

    def get_or_create_room(self, room_name):
        return 'bla'
