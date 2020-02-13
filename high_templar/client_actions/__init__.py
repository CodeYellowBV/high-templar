async def handle_message(connection, message):
    """
    Handle an incomming message from the connection, and handle them accordingly.
    """

    if message == 'ping':
        return await connection.send_raw('pong')
