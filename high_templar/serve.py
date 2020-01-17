#!/usr/bin/env python3
import os, logging

import werkzeug
from main import create_app
from connection import header

class Settings:
    API_URL = os.environ.get('CY_BINDER_INTERNAL', 'http://localhost:8000/api/')
    USER_ID_PATH = ['user', 'data', 'id']
    FORWARD_IP = 'HTTP_X_REAL_IP'
    CONNECTION_HEADERS = {
        'X-Session-Token': header.Param('session_token'),
    }
    RABBITMQ = {
        'enabled': False,
        'exchange_name': 'hightemplar',
        'username': 'rabbitmq',
        'password': 'rabbitmq',
        'host': 'rabbitmq'

    }


app = create_app(Settings)
app.logger.setLevel(logging.DEBUG)


if __name__ == '__main__':
    from gevent import pywsgi, monkey
    from geventwebsocket.handler import WebSocketHandler


    @werkzeug.serving.run_with_reloader
    def run():
        app.debug = True
        print('Running server')
        server = pywsgi.WSGIServer(('', 5000), app, handler_class=WebSocketHandler)
        monkey.patch_all()
        server.serve_forever()
    run()