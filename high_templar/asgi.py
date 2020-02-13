import os, logging
from main import create_app
# from connection import header


class Settings:
    API_URL = os.environ.get('CY_BINDER_INTERNAL', 'http://wiremock:8080/api/')
    USER_ID_PATH = ['user', 'data', 'id']
    FORWARD_IP = 'HTTP_X_REAL_IP'
    CONNECTION_HEADERS = {
        # 'X-Session-Token': header.Param('session_token'),
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


application = app