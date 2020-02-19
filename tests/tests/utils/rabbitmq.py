import pika
from pika import BlockingConnection
from pika.adapters.asyncio_connection import AsyncioConnection

from settings import RABBITMQ as config

connection_credentials = pika.PlainCredentials(config['username'], config['password'])
connection_parameters = pika.ConnectionParameters(config['host'], credentials=connection_credentials)
connection = BlockingConnection(parameters=connection_parameters)
channel = connection.channel()


def send_trigger(message):
    channel.basic_publish('hightemplar', routing_key='*', body='')
    pass
