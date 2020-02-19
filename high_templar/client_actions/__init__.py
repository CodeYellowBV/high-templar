import json
from json import JSONDecodeError

from .ping import ping
from .subscribe import subscribe
from .unsubscribe import unsubscribe

# Registered actions callbacks
ACTIONS = {
    'subscribe': subscribe,
    'unsubscribe': unsubscribe
}


async def handle_message(connection, message: str):
    """
    Handle an incomming message from the connection, and handle them accordingly.
    """

    if message == 'ping':
        return await ping(connection, message)

    try:
        message_content = json.loads(message)
    except JSONDecodeError:
        return await connection.send({
            'requestId': connection.ID,
            'code': 'error',
            'message': 'non-json-message',
        })
    action = message_content.get('type', None)

    if action not in ACTIONS:
        connection.app.logger.info("{}: Unsupported action".format(connection.ID, action))
        return await connection.send({
            'requestId': connection.ID,
            'code': 'error',
            'message': 'message-type-not-allowed',
        })
    return await ACTIONS[action](connection, message_content)
