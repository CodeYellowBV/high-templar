import asyncio
from datetime import datetime

from high_templar.connection import Connection

from high_templar.authentication import Permission
import json
from high_templar.subscription import Subscription
from quart import Quart
import logging

logger = logging.getLogger()

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
    A room keeps track of all subscriptions with the same scoped permission.
    In the case a view_action.own, all subscriptions would belong to the same connection
    """

    def __init__(self, app: Quart, permission: Permission):
        # mapping between (connection.Id,  => connection
        self.app = app
        self.permission = permission
        self.subscriptions = set()

    def add_subscription(self, subscription: Subscription):
        self.subscriptions.add(subscription)

    def remove_subscription(self, subscription: Subscription) -> bool:
        """
        Remove a connection. Returns a boolean indicating that the room should be removed
        :param subscription:
        :return: Should the room be removed
        """
        self.app.logger.debug(f'room.remove_subscription: {subscription}')
        if subscription not in self.subscriptions:
            raise NotSubscribedException()

        self.subscriptions.discard(subscription)

        return len(self.subscriptions) == 0


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

        # mapping of connection => subscriptions
        self.subscriptions = {}

        # mapping of permission  => room
        self.rooms = {}

    def register(self, connection: Connection):
        """
        "Registers a connection
        """
        self.subscriptions[connection] = set()

    def deregister(self, connection: Connection):
        # Unsubscribe from all rooms
        connection.app.logger.debug(f'HUB: Deregistering {connection.ID}')
        subscriptions = list(self.subscriptions.get(connection, []))
        connection.app.logger.debug(f'HUB: Deregistering subscriptions {str(subscriptions)}')
        for subscription in subscriptions:
            try:
                self.unsubscribe(subscription)
            except NotSubscribedException:
                pass

        # Note that if we deregister, it doesn't necessarily mean that the connection is registered. Hence the safety
        # checks
        if connection in self.subscriptions:
            del self.subscriptions[connection]

    def subscribe(self, subscription: Subscription) -> bool:
        """
        Subscribe a connection to a subscription. Returns
        :param connection:
        :param subscription:
        :return:
        """

        if not subscription.connection.authentication.has_permission(subscription.permission):
            raise NoPermissionException()

        if subscription.permission.hash() in self.rooms:
            room = self.rooms[subscription.permission.hash()]
            self.app.logger.debug("HUB: Reuse room {}".format(room.permission))
        else:
            room = Room(self.app, subscription.permission)
            self.app.logger.debug("HUB: Created room {}".format(room.permission))
            self.rooms[subscription.permission.hash()] = room


        self.subscriptions[subscription.connection].add(subscription)
        room.add_subscription(subscription)

    def unsubscribe(self, subscription: Subscription):
        if subscription.permission.hash() not in self.rooms:
            raise NotSubscribedException()
        room = self.rooms[subscription.permission.hash()]

        room_empty = room.remove_subscription(subscription)
        if room_empty:
            self.app.logger.debug("HUB: Deleted room {}".format(room.permission))
            del self.rooms[room.permission.hash()]
        else:
            self.app.logger.debug(
                "HUB: Kept room {}. Alive subscriptions: {}".format(room.permission, len(room.subscriptions)))

    def status(self):
        """
        Provides a full status report of the hub.
        :return:
        """

        num_connections = len(self.subscriptions)
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

            # Send the message to all connections as a seperate event
            send_data_futures = []

            async def send_message(subscription, data):
                connection = subscription.connection
                connection.app.hub.hub_status.ws_messages_send_queued += 1

                try:
                    await connection.send({
                        "type": "publish",
                        "data": data,
                        "requestId": subscription.request_id
                    })
                    connection.app.hub.hub_status.ws_messages_send += 1
                except Exception as e:
                    connection.app.hub.hub_status.ws_messages_send_error += 1
                    connection.app.logger.warning("Error when sending message: {}".format(e))


            for permission in message_permissions:
                if permission.hash() in self.rooms:
                    for subscription in self.rooms[permission.hash()].subscriptions:
                        try:
                            send_data_futures.append(send_message(subscription, data))
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
