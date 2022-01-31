import asyncio


async def ping(connection, message):
    return await asyncio.gather(
        connection.send_raw('pong'),
        connection.app.notify_ping(connection)
    )
