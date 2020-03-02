from high_templar.authentication import Permission
from high_templar.subscription import Subscription


async def unsubscribe(connection, message):
    from high_templar.hub import NotSubscribedException
    permission = Permission(message['room'])

    if 'requestId' not in message:
        return await connection.send({
            "code": "error",
            "message": "no-request-id"
        })

    try:
        connection.app.hub.unsubscribe(
            Subscription(
                connection=connection,
                permission=permission,
                request_id=message['requestId']
            )
        )
    except NotSubscribedException:
        return await connection.send({
            "code": "error",
            "message": "not-subscribed"
        })

    await connection.send({
        'code': 'success',
    })
