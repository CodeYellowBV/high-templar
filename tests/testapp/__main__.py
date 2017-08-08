# For some reason, the test discovery also reads this file
# When the tests loader runs it, it doesn't accept "from app import app":
# SystemError: Parent module '' not loaded, cannot perform relative import

if __name__ == '__main__':
    from gevent import pywsgi, monkey
    from geventwebsocket.handler import WebSocketHandler
    from app import app

    print('Running server')
    server = pywsgi.WSGIServer(('', 5000), app, handler_class=WebSocketHandler)
    monkey.patch_all()
    server.serve_forever()
