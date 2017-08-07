from app import app
from gevent import pywsgi, monkey
from geventwebsocket.handler import WebSocketHandler

print('Running server')
server = pywsgi.WSGIServer(('', 5000), app, handler_class=WebSocketHandler)
monkey.patch_all()
server.serve_forever()
