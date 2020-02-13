import asyncio

from quart import Quart, request, make_response, websocket
import logging
import json
import gevent

from connection import Connection
from backend_adapter import BinderAdapter

global_state = 0


def create_app(settings=None):
    app = Quart(__name__)

    if settings:
        app.config.from_object(settings)

    # For now, just use the binderadapter
    backend_adapter = BinderAdapter(app)

    @app.websocket('/ws/')
    async def open_socket():
        # Get out of the global context, and get the actual websocket connection, such that we can understand
        # what is going
        ws = websocket._get_current_object()
        connection = Connection(backend_adapter, app, ws)
        await connection.run()

    @app.route('/trigger/', methods=['POST'])
    async def handle_trigger():
        data = json.loads(request.data.decode())
        return app.hub.handle_trigger(data)

    return app
