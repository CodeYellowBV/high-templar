import pika
import uuid
import logging
import time
import json

from pika.adapters.asyncio_connection import AsyncioConnection

logger = logging.getLogger(__name__)
queue_id = uuid.uuid4()
QUEUE_NAME = 'hightemplar_{}'.format(queue_id)


def consumer_factory(app):
    """
    Factory to inject the app context
    :param app:
    :return:
    """

    def consume(channel, method, properties, body):
        try:
            data = json.loads(body)
            with app.app_context():
                app.hub.handle_trigger(data)
            channel.basic_ack(delivery_tag=method.delivery_tag)
        except Exception as e:
            logger.error("Exception during handling of {}".format(body))
            logger.error(e)
            # Don't requeue. This will fill the queue again, and slow down the whole of HT, and we can't fix the error
            # anyways, since the queue is not durable
            channel.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

    return consume


def start_consuming(app):
    config = app.config.get('RABBITMQ')
    # Get a random id for this queue, such that every process/thread has their own queue

    exchange_name = config['exchange_name']

    connection_credentials = pika.PlainCredentials(config['username'], config['password'])
    connection_parameters = pika.ConnectionParameters(config['host'], credentials=connection_credentials)
    connection = AsyncioConnection(parameters=connection_parameters)
    channel = connection.channel()
    channel.exchange_declare(exchange_name)
    channel.queue_declare(QUEUE_NAME, durable=False)
    channel.queue_bind(queue=QUEUE_NAME, exchange=exchange_name,
                       routing_key='*')
    channel.basic_consume(on_message_callback=consumer_factory(app), queue=QUEUE_NAME)
    channel.start_consuming()


async def run(app):
    """
    Creates a queue, and attaches it to the exchange. Then listens to messages on the queue, and handles them
    :return:
    """
    config = app.config.get('RABBITMQ')

    if not config['enabled']:
        logger.info('Rabbitmq not enabled. Not listening')
        return
    logger.info('Rabbitmq enabled. Start listening')

    while True:
        try:
            start_consuming(app)
        except Exception as e:
            logger.error(e)
            logger.error("Serious error. Trying again in a few seconds ")
        time.sleep(10)

    app.logger.debug("START RABBIT<Q!")
