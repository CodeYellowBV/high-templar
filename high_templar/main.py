from flask_sockets import Sockets
from flask import Flask, request
import logging
import json


def create_app(settings=None):
    app = Flask(__name__)

    if settings:
        app.config.from_object(settings)

    sockets = Sockets(app)

    from .hub import Hub
    app.hub = Hub(app)

    @sockets.route('/ws/')
    def open_socket(ws):
        connection = app.hub.add_if_auth(ws)
        if not connection:
            # todo manage connection close
            return

        for hook in app.hub.connect_hooks:
            hook(connection)

        while not connection.ws.closed:
            message = connection.ws.receive()
            if message:
                try:
                    connection.handle(message)
                except Exception as e:
                    logging.error(e, exc_info=True)

        for hook in app.hub.disconnect_hooks:
            hook(connection)

    @app.route('/trigger/', methods=['POST'])
    def handle_trigger():
        data = json.loads(request.data.decode())
        return app.hub.handle_trigger(data)

    return app
