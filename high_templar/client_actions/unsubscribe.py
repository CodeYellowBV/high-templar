from high_templar.authentication import Permission


async def unsubscribe(connection, message):
    from high_templar.hub import NotSubscribedException
    permission = Permission(message['room'])

    try:
        connection.app.hub.unsubscribe(
            connection, permission
        )
    except NotSubscribedException:
        return await connection.send({
            "code": "error",
            "message": "not-subscribed"
        })

    await connection.send({
        'code': 'success',
    })
