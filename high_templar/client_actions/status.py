async def status(connection, message):
    return await connection.send(
        connection.app.hub.status()
    )