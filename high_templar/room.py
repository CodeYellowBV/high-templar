import json


class WebSocketClosedError(Exception):
    pass


class Subscription:
    '''
    A subscription of a connection to a room
    '''

    def __init__(self, connection, room, request):
        self.connection = connection
        self.room = room
        self.requestId = request['requestId']
        self.scope = request.get('scope', {})

    def publish(self, data):
        if self.connection.ws.closed:
            raise WebSocketClosedError

        self.connection.ws.send(json.dumps({
            'requestId': self.requestId,
            'type': 'publish',
            'data': data,
        }))

    def stop(self):
        self.room.remove_subscription(self)


class Room:
    '''
    A collection of subscriptions which have access to a scoped permission.

    A permission would be: See actions
    A scoped permission would be: See your own actions

    Then there would "exist" a room for every single user with view_action.own scoped permission
    "exist" between quotation marks, because high-templar only creates a room when someone actually subscribes to it.

    A room keeps track of all connections with the same scoped permission.
    In the case a view_action.own, it would have a maximum of 1 connection.
    '''

    def __init__(self, hash, hub):
        self.hash = hash
        self.hub = hub
        self.subscriptions = []

    def subscribe(self, connection, request):
        sub = Subscription(connection, self, request)
        self.subscriptions.append(sub)
        return sub

    # Don't just unsubscribe: remove all subscriptions for a connection
    def remove_connection(self, connection):
        # Clone self.subscriptions because they may be removed when closed
        for s in list(self.subscriptions):
            if s.connection == connection:
                self.subscriptions.remove(s)

        self.close_if_empty()

    def remove_subscription(self, sub):
        self.subscriptions.remove(sub)

        self.close_if_empty()

    def close_if_empty(self):
        if not self.subscriptions:
            self.close()

    def close(self):
        self.hub.close_room(self)

    # Returns a list of closed connections
    def publish(self, data):
        closed_connections = []
        for s in self.subscriptions:
            try:
                s.publish(data)
            except WebSocketClosedError:
                closed_connections.append(s.connection)

        return closed_connections

    @property
    def connections(self):
        return [s.connection for s in self.subscriptions]

    # Room names are dict.
    # Every keyval pair is a scope of the permission.
    # IE:
    # { 'zoo': 1, 'animal_type': 'penguin'}
    # Is a room where publishes about the penguins in zoo 1 appear.
    #
    # The backend needs to dictate which rooms a user can be in,
    # and the frontend needs to programmatically define the room to subscribe to.
    #
    # We hash the dicts so that
    # {'foo': True, 'bar': True} is the same room as {'bar': True, 'foo': True}
    # and so we can still check if a room exists
    @staticmethod
    def hash_dict(room_dict):
        return json.dumps(room_dict, sort_keys=True)
