#!/usr/bin/env python3
from gevent import pywsgi, monkey

if __name__ == '__main__':
    monkey.patch_all()

import os, logging

import werkzeug
from main import create_app
from connection import header

class Settings:
    API_URL = os.environ.get('CY_BINDER_INTERNAL', 'http://nginx:8001/api/')
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

fh = logging.FileHandler('backend.log')
fh.setLevel(logging.DEBUG)

app.logger.addHandler(fh)


if __name__ == '__main__':
    from gevent import pywsgi, monkey
    from geventwebsocket.handler import WebSocketHandler


    @werkzeug.serving.run_with_reloader
    def run():
        app.logger.debug('Start server!')
        app.debug = True
        print('Running server')
        server = pywsgi.WSGIServer(('', 5000), app, handler_class=WebSocketHandler)
        server.serve_forever()
    run()