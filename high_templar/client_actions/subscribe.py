from authentication import Permission


async def subscribe(connection, message):
    permission = Permission(message['room'])

    connection.app.hub.subscribe(
        connection, permission
    )
    return await connection.send({
        'requestId': connection.ID,
        'code': 'success',
    })
