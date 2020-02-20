import asyncio

from quart import Quart, request, make_response, websocket
import json

from high_templar.connection import Connection
from high_templar.backend_adapter import BinderAdapter
from high_templar.rabbitmq import run as run_rabbitmq

from high_templar.hub import Hub


class HTQuart(Quart):
    """
    Patch for the quart server, such that the worker joins the futures of the asgi server and the rabbitmq,
    this allows us to both listen to rabbitmq, as well as handle the connection at the same time
    """

    IS_STARTED = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.connect_hooks = []
        self.ping_hooks = []
        self.disconnect_hooks = []

    async def status(self):
        HTQuart.IS_STARTED = True
        while True:
            await asyncio.sleep(5)
            self.hub.status()

    async def background(self):
        if HTQuart.IS_STARTED:
            return
        HTQuart.IS_STARTED = True

        return await asyncio.gather(
            run_rabbitmq(self),
            self.status()
        )

    async def __call__(self, *args, **kwargs):
        """
        We need to hook into the background task somehow. We currently do this here, but that might not be the best place
        to do it, since this seems to be called more than once. Hence the hack in background() which checksn if
        the background is already started.
        """
        return await asyncio.gather(
            super().__call__(*args, **kwargs),
            self.background()
        )

    def on_connect(self, func):
        self.connect_hooks.append(func)
        return func

    def on_ping(self, func):
        self.ping_hooks.append(func)
        return func

    def on_disconnect(self, func):
        self.disconnect_hooks.append(func)
        return func

    async def notify_connect(self, connection):
        await asyncio.gather(
            *[
                hook(connection) for hook in self.connect_hooks
            ]
        )

    async def notify_ping(self, connection):
        await asyncio.gather(
            *[
                hook(connection) for hook in self.ping_hooks
            ]
        )

    async def notify_disconnect(self, connection):
        await asyncio.gather(
            *[
                hook(connection) for hook in self.disconnect_hooks
            ]
        )


def create_app(settings=None):
    app = HTQuart(__name__)
    app.hub = Hub(app)

    if settings:
        app.config.from_object(settings)

    # For now, just use the binderadapter

    @app.websocket('/ws/')
    async def open_socket():
        # Get out of the global context, and get the actual websocket connection, such that we can understand
        # what is going
        ws = websocket._get_current_object()
        connection = Connection(BinderAdapter(app), app, ws)
        notify_future = app.notify_connect(connection)
        try:
            await asyncio.gather(
                connection.run(),
                notify_future
            )
        finally:
            app.logger.debug("Closed socket, deregister!: {}".format(connection.ID))
            app.hub.deregister(connection)
        await app.notify_disconnect(connection)

    # @app.route('/trigger/', methods=['POST'])
    # async def handle_trigger():
    #     data = json.loads(request.data.decode())
    #     return app.hub.handle_trigger(data)

    return app
