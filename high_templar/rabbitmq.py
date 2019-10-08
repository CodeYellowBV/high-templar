import pika
import uuid
import logging
import time
import json

logger = logging.getLogger(__name__)


def consumer_factory(app):
    """
    Factory to inject the app context
    :param app:
    :return:
    """

    def consume(channel, method, properties, body):
        try:
            data = json.loads(body)
            app.hub.handle_trigger(data)
        except Exception as e:
            logger.error("Exception during handling of {}".format(body))
            logger.error(e)
            # Don't requeue. This will fill the queue again, and slow down the whole of HT, and we can't fix the error
            # anyways, since the queue is not durable
            channel.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

    return consume


def start_consuming(app):
    # Get a random id for this queue, such that every process/thread has their own queue
    queue_id = uuid.uuid4()
    queue_name = 'hightemplar_{}'.format(queue_id)
    exchange_name = 'hightemplar'

    connection_credentials = pika.PlainCredentials('rabbitmq', 'rabbitmq')
    connection_parameters = pika.ConnectionParameters('localhost', credentials=connection_credentials)
    connection = pika.SelectConnection()

    channel = connection.channel()
    channel.queue_declare(queue_name, durable=False)
    channel.queue_bind(queue=queue_name, exchange=exchange_name,
                       routing_key='*')
    channel.basic_consume(consumer_factory(app), queue=queue_name, no_ack=False)


def run(app):
    """
    Creates a queue, and attaches it to the exchange. Then listens to messages on the queue, and handles them
    :return:
    """
    while True:
        try:
            start_consuming(app)
        except Exception as e:
            logger.error(e)
            logger.error("Serious error. Trying again in a few seconds ")
            time.sleep(10)
