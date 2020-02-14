async def ping(connection, message):
    return await connection.send_raw('pong')