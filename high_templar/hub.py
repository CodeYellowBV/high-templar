import asyncio
from datetime import datetime

from connection import Connection

from authentication import Permission
import json


class NoPermissionException(Exception):
    pass


class NotSubscribedException(Exception):
    pass


class Room:
    """
    A collection of subscriptions which have access to a scoped permission.
    A permission would be: See actions
    A scoped permission would be: See your own actions
    Then there would "exist" a room for every single user with view_action.own scoped permission
    "exist" between quotation marks, because high-templar only creates a room when someone actually subscribes to it.
    A room keeps track of all connections with the same scoped permission.
    In the case a view_action.own, it would have a maximum of 1 connection.
    """

    def __init__(self, subscription: Permission):
        # mapping between connection.Id => connection
        self.subscription = subscription
        self.connections = {}

    def add_connection(self, connection):
        self.connections[connection.ID] = connection

    def remove_connection(self, connection) -> bool:
        """
        Remove a connection. Returns a boolean indicating that the room should be removed
        :param connection:
        :return: Should the room be removed
        """
        if connection.ID not in self.connections:
            raise NotSubscribedException()

        del self.connections[connection.ID]

        return len(self.connections) == 0


class Status:
    """
    Object taking care of status information of the hub
    """

    def __init__(self):
        self.created_at = datetime.now()
        self.rabbitmq_messages_received = 0

        # how many messages have been send
        self.ws_messages_send = 0

        # How many ws messages have been queued in general (so are either send, or are send, but not received yet
        self.ws_messages_send_queued = 0
        self.ws_messages_send_error = 0
        self.ws_messages_received = 0


class Hub:
    """
    Manages all connections, and distributes incoming triggers
    """

    def __init__(self, app):
        self.hub_status = Status()
        self.app = app

        # mapping of connection.ID => connection object
        self.connections = {}

        # mapping of connection => set of routing keys
        self.subscriptions = {}

        # mapping of routing key => room
        self.rooms = {}

    def register(self, connection: Connection):
        """
        "Registers a connection
        """
        self.connections[connection.ID] = connection
        self.subscriptions[connection.ID] = set()

    def deregister(self, connection: Connection):
        # Unsubscribe from all rooms
        connection.app.logger.debug("HUB: Deregistering {}.".format(connection.ID))
        subscriptions = list(self.subscriptions.get(connection.ID, []))
        for subscription in subscriptions:
            try:
                self.unsubscribe(connection, subscription)
            except NotSubscribedException:
                pass

        # Note that if we deregister, it doesn't necessarily mean that the connection is registered. Hence the safety
        # checks
        if connection.ID in self.subscriptions:
            del self.subscriptions[connection.ID]
        if connection.ID in self.connections:
            del self.connections[connection.ID]

    def subscribe(self, connection: Connection, subscription: Permission) -> bool:
        """
        Subscribe a connection to a subscription. Returns
        :param connection:
        :param subscription:
        :return:
        """

        if not connection.authentication.has_permission(subscription):
            raise NoPermissionException()

        if subscription in self.rooms:
            room = self.rooms[subscription]
        else:
            room = Room(subscription)
            self.app.logger.debug("HUB: Created room {}".format(room.subscription))
            self.rooms[subscription] = room

        self.subscriptions[connection.ID].add(subscription)
        room.add_connection(connection)

    def unsubscribe(self, connection: Connection, subscription: Permission):
        if subscription not in self.rooms:
            raise NotSubscribedException()
        room = self.rooms[subscription]

        self.subscriptions[connection.ID].remove(subscription)

        room_empty = room.remove_connection(connection)
        if room_empty:
            self.app.logger.debug("HUB: Deleted room {}".format(room.subscription))
            del self.rooms[subscription]
        else:
            self.app.logger.debug(
                "HUB: Kept room {}. Alive subscriptions: {}".format(room.subscription, len(room.connections)))

    def status(self):
        """
        Provides a full status report of the hub.
        :return:
        """

        num_connections = len(self.connections)
        num_rooms = len(self.rooms)
        online_since = self.hub_status.created_at.isoformat()
        online_time_str = datetime.now() - self.hub_status.created_at
        ws_messages_queued = self.hub_status.ws_messages_send_queued - self.hub_status.ws_messages_send_error - self.hub_status.ws_messages_send

        self.app.logger.info("""
        STATUS: \n
        open connections: {}
        num_rooms: {}
        online_since: {} ({})
        messages_received (rabbitmq, total): {}
        messages_received (ws, total): {}
        messages_send (ws, total): {}
        messages_send (ws, error): {}
        messages_send (ws, queue): {}
        """.format(num_connections, num_rooms, online_since, online_time_str,
                   self.hub_status.rabbitmq_messages_received,
                   self.hub_status.ws_messages_send,
                   self.hub_status.ws_messages_received,
                   self.hub_status.ws_messages_send_error, ws_messages_queued))

        return {
            "open_connections": num_connections,
            "num_rooms": num_rooms,
            "online_since": online_since,
            "rabbitmq_messages_received": self.hub_status.rabbitmq_messages_received,
            "ws_messages_received": self.hub_status.ws_messages_received,
            "ws_messages_send": self.hub_status.ws_messages_send,
            "ws_messages_send_error": self.hub_status.ws_messages_send_error,
            "ws_messages_send_queued": ws_messages_queued
        }

    async def dispatch_message(self, message):
        self.hub_status.rabbitmq_messages_received += 1
        try:
            self.app.logger.info("Dispatch message: {}".format(message))
            content = json.loads(message)

            message_permissions = list(
                map(lambda x: Permission(x), content['rooms'])
            )
            data = content['data']

            rooms_to_dispatch_to = []

            # Get all the rooms for which this message may be important
            for room in self.rooms.values():
                # Check all the rooms for those which have a permission to this message, and (maybe) nmore
                for permission in message_permissions:
                    self.app.logger.debug("{} {}".format(type(permission), type(room.subscription)))
                    if permission <= room.subscription:
                        rooms_to_dispatch_to.append(room)
                        break

            # Get all the connections to dispatch to:
            connections_to_dispatch_to = set().union(*[set(room.connections.keys()) for room in rooms_to_dispatch_to])

            # Send the message to all connections as a seperate event
            send_data_futures = []

            async def send_message(connection, data):
                connection.app.hub.hub_status.ws_messages_send_queued += 1

                try:
                    await self.connections[connection.ID].send(data)
                    connection.app.hub.hub_status.ws_messages_send += 1
                except Exception as e:
                    connection.app.hub.hub_status.ws_messages_send_error += 1
                    connection.app.logger.warning("Error when sending message: {}".format(e))

            self.app.logger.debug("Dispatch message to {} connections".format(len(connections_to_dispatch_to)))
            self.app.logger.debug("Sending message to {}".format(connections_to_dispatch_to))

            for connection_id in connections_to_dispatch_to:
                try:
                    send_data_futures.append(send_message(self.connections[connection_id], data))
                except KeyError:
                    # Happens if the connection with connection_id has been disconnected.
                    pass

            await asyncio.gather(*send_data_futures)

        except Exception as e:
            """
            Make sure that all errors are caught, such that we do not crash the whole thread
            """
            self.app.logger.error(e)
            return
