from high_templar.authentication import Permission
from high_templar.subscription import Subscription


async def subscribe(connection, message):
    from high_templar.hub import NoPermissionException
    permission = Permission(message['room'])

    if 'requestId' not in message:
        return await connection.send({
            "code": "error",
            "message": "no-request-id"
        })

    try:
        connection.app.hub.subscribe(
            Subscription(
                connection=connection,
                permission=permission,
                request_id=message['requestId']
            )
        )
    except NoPermissionException:
        return await connection.send({
            "code": "error",
            "message": "room-not-found"
        })

    await connection.send({
        'code': 'success',
    })
