from flask import Flask
import logging
from flask_sockets import Sockets


def create_app(settings=None):
    app = Flask(__name__)

    if settings:
        app.config.from_object(settings)

    sockets = Sockets(app)

    from .hub import Hub
    app.hub = Hub(app)

    @sockets.route('/ws/')
    def open_socket(ws):
        auth = app.hub.add_if_auth(ws)
        if not auth:
            # todo manage socket close
            return

        socket = auth
        while not socket.ws.closed:
            message = socket.ws.receive()
            if message:
                try:
                    socket.handle(message)
                except Exception as e:
                    logging.error(e, exc_info=True)

    return app
