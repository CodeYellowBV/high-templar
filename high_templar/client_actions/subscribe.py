async def subscribe(connection, message):
    return await connection.send({
        'requestId': connection.ID,
        'code': 'success',
    })