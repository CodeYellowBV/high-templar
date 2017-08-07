#!/usr/bin/env python3
from flask_script import Manager
from app import create_app
from settings import Settings
from werkzeug.serving import run_with_reloader
import logging

app = create_app(Settings)
manager = Manager(app)


@manager.command
def runserver():
    from gevent import pywsgi, monkey
    from geventwebsocket.handler import WebSocketHandler
    server = pywsgi.WSGIServer(('', 5000), app, handler_class=WebSocketHandler)

    if app.debug:
        logging.basicConfig(format='%(asctime)s %(message)s')
        logger = logging.getLogger()
        logger.setLevel(logging.DEBUG)
        monkey.patch_all()
        run_with_reloader(server.serve_forever)
    else:
        server.serve_forever()


if __name__ == '__main__':
    manager.run()
