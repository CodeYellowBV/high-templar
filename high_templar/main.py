import asyncio

from quart import Quart, request, make_response, websocket
import json

from connection import Connection
from backend_adapter import BinderAdapter
from rabbitmq import run as run_rabbitmq

from hub import Hub


class HTQuart(Quart):
    """
    Patch for the quart server, such that the worker joins the futures of the asgi server and the rabbitmq,
    this allows us to both listen to rabbitmq, as well as handle the connection at the same time
    """

    async def status(self):
        while True:
            await asyncio.sleep(100)
            self.hub.status()

    async def __call__(self, *args, **kwargs):
        return await asyncio.gather(
            super().__call__(*args, **kwargs),
            run_rabbitmq(self),
            self.status()
        )


def create_app(settings=None):
    app = HTQuart(__name__)
    app.hub = Hub(app)

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
        try:
            await connection.run()
        finally:
            app.hub.deregister(connection)

    @app.route('/trigger/', methods=['POST'])
    async def handle_trigger():
        data = json.loads(request.data.decode())
        return app.hub.handle_trigger(data)

    return app
