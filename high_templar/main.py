import asyncio

from quart import Quart, request, make_response, websocket
import logging
import json
import gevent

global_state = 0

def create_app(settings=None):
    app = Quart(__name__)

    if settings:
        app.config.from_object(settings)

    from hub import Hub
    app.hub = Hub(app)

    @app.websocket('/ws/')
    async def open_socket():

        global global_state
        global_state += 1
        # ?????
        ws = websocket
        ws.environ = {}
        ws.closed =  False
        app.logger.info(f"open {global_state}")
        connection = app.hub.add_if_auth(ws, app)


        if not connection:
            # todo manage connection close
            return

        for hook in app.hub.connect_hooks:
            hook(connection)

        def process(connection, message):
            if message:
                try:
                    connection.handle(message)
                except Exception as e:
                    logging.error(e, exc_info=True)

        while not connection.ws.closed:
            message = connection.ws.receive()
            asyncio.spawn(process, connection, message)

        for hook in app.hub.disconnect_hooks:
            hook(connection)

    @app.route('/trigger/', methods=['POST'])
    async def handle_trigger():
        data = json.loads(request.data.decode())
        return app.hub.handle_trigger(data)

    return app
