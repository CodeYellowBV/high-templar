if __name__ == '__main__':
    from main import create_app

    class Config:
        def __init__(self):
            self.API_URL = 'foo/bar'
            self.RABBITMQ = {
                'enabled': True,
                'exchange_name': 'hightemplar',
                'username': 'rabbitmq',
                'password': 'rabbitmq',
                'host': 'localhost'
            }

    app = create_app(Config())

    from gevent import pywsgi, monkey
    from geventwebsocket.handler import WebSocketHandler

    print('Running server')
    server = pywsgi.WSGIServer(('', 8000), app, handler_class=WebSocketHandler)
    server.serve_forever()
