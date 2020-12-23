import asyncio
import json
import uuid

from high_templar.backend_adapter.interface import BackendConnectionException

from high_templar.client_actions import handle_message


class Connection:
    """
    A websocket connection that is able to send and retrieve messages
    """

    def __init__(self, backend_adapter, app, websocket):
        self.backend_adapter = backend_adapter
        self.app = app
        self.websocket = websocket
        self.authentication = None

        # Create an identification for the connection for debugging and such
        self.ID = str(uuid.uuid4())

        self.app.logger.debug("{} Created connection".format(self.ID))
        self.app.logger.debug("{} Headers: {}".format(self.ID, self.websocket.headers))

    async def send(self, message: dict):
        """
        Send a json encoded message to the websocket client, appended with the connection id
        :param message:
        :return:
        """
        return await self.send_raw(json.dumps(message))

    async def send_raw(self, message: str):
        self.app.logger.debug("{} send message: {}".format(self.ID, message))
        return await self.websocket.send(message)

    async def authenticate(self) -> bool:
        self.app.logger.debug("{} Check if connection is authenticated".format(self.ID))
        try:
            self.authentication = await self.backend_adapter.get_authentication(self.websocket)
            self.app.logger.debug("{} Successfully authenticated. Response: {}".format(self.ID, self.authentication))

            # TODO: Send allowed rooms
            await self.send({
                "is_authorized": True,
                'allowed_rooms': self.authentication.json_serializable()
            })
            return True

        except BackendConnectionException:
            self.app.logger.debug("{} Not authenticated".format(self.ID))
            return False

    async def listen(self):
        """
        Listen to actions from the user, and handle them
        :return:
        """
        try:
            while True:
                # Add a timeout to the connection. If we do not receive a ping for a while, close the connection
                # This makes sure that connections which are not properly closed are cleaned up
                message = await asyncio.wait_for(self.websocket.receive(), 300)
                self.app.logger.debug("{} received message: {}".format(self.ID, message))
                await handle_message(self, message)
        except asyncio.TimeoutError:
            # Too long without a response, close the connection
            pass

    async def run(self):
        # First check if we are authenticated
        if not await self.authenticate():
            await self.send({'is_authorized': False})
            # Need a bit of grace time, to allow the other side to actually receive the message before the connection
            # is broken
            await asyncio.sleep(0.1)
            return

        # Register the connection at the hub
        self.app.hub.register(self)

        await self.listen()

    def __str__(self):
        return "<Connection id={}>" .format(self.ID)