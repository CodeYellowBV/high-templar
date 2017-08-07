from settings import Settings
from flask import Flask
import logging
from flask_sockets import Sockets


def create_app(settings=None):
    app = Flask(__name__)

    if settings:
        app.config.from_object(Settings)

    sockets = Sockets(app)

    from chimera.hub import Hub
    hub = Hub()

    @sockets.route('/api/')
    def open_socket(ws):
        socket = hub.add(ws)
        while not socket.ws.closed:
            message = socket.ws.receive()
            if message:
                try:
                    socket.handle(message)
                except Exception as e:
                    logging.error(e, exc_info=True)
