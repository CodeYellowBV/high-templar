#!/usr/bin/env python3
import os
import logging

from high_templar.main import create_app
from high_templar.backend_adapter import header
from dotenv import load_dotenv, find_dotenv


load_dotenv(os.environ.get('ENV_FILE', find_dotenv()))
app_url = os.environ.get('APP_URL', '') + '/api/'
log_file = os.environ.get('LOGFILE_PATH', 'hightemplar.log')
logging.basicConfig(
    level=os.environ.get('LOGFILE_LEVEL', logging.DEBUG),
    filename=log_file,
    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
    datefmt='%m-%d %H:%M',
)


class Settings:
    API_URL = os.environ.get('BINDER_INTERNAL', app_url)
    USER_ID_PATH = ['user', 'data', 'id']
    FORWARD_IP = 'HTTP_X_REAL_IP'
    CONNECTION_HEADERS = {
        'X-Session-Token': header.Param('session_token'),
        'Referer': header.Fixed(app_url), # Needed in production for online/offline notification (see T25664)
    }
    RABBITMQ = {
        'enabled': True,
        'exchange_name': 'hightemplar',
        'username':  os.environ.get('RABBITMQ_USERNAME', 'rabbitmq'),
        'password': os.environ.get('RABBITMQ_PASSWORD', 'rabbitmq'),
        'host': os.environ.get('RABBITMQ_HOST', 'localhost'),
    }


app = create_app(Settings)


@app.on_connect
@app.on_ping
async def notify_online(connection):
    connection.app.logger.debug("Notify online")
    await connection.backend_adapter.post('user/notify_online/')


@app.on_disconnect
async def notify_offline(connection):
    connection.app.logger.debug("Notify offline")
    await connection.backend_adapter.post('user/notify_offline/')
