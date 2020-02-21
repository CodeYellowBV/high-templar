import asyncio

import uuid
import logging
import aio_pika

logger = logging.getLogger(__name__)
queue_id = uuid.uuid4()
QUEUE_NAME = 'hightemplar_{}'.format(queue_id)


async def run(app):
    """
    Creates a queue, and attaches it to the exchange. Then listens to messages on the queue, and handles them
    :return:
    """
    app.logger.debug("START RABBITMQ ")
    config = app.config.get('RABBITMQ')

    app.logger.debug(config)

    while True:
        loop = asyncio.get_event_loop()

        try:
            app.logger.debug("Create connection!")
            connection = await aio_pika.connect_robust(
                "amqp://rabbitmq:rabbitmq@rabbitmq", loop=loop
            )
            # Creating channel
            app.logger.debug("Create channel")
            channel = await connection.channel()
            async with connection:
                app.logger.debug("create exchange")
                await channel.declare_exchange(config['exchange_name'])

                queue = await channel.declare_queue(
                    QUEUE_NAME, auto_delete=True, durable=False
                )
                await queue.bind(exchange=config['exchange_name'], routing_key='*')

                async with queue.iterator() as queue_iter:
                    async for message in queue_iter:
                        async with message.process():
                            content = message.body.decode()
                            app.logger.debug("RABBITMQ: got message {}".format(content))
                            loop = asyncio.get_event_loop()
                            loop.create_task(app.hub.dispatch_message(content))
        except Exception as e:
            app.logger.error("Exception in connection with rabbitmq. Back of a bit, and try again")
            app.logger.exception(e)
            await asyncio.sleep(3)
