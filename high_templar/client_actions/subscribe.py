from authentication import Permission


async def subscribe(connection, message):
    from hub import NoPermissionException
    permission = Permission(message['room'])

    try:
        connection.app.hub.subscribe(
            connection, permission
        )
    except NoPermissionException:
        return await connection.send({
            "code": "error",
            "message": "room-not-found"
        })

    await connection.send({
        'code': 'success',
    })
