#!/usr/bin/env python3
from high_templar.main import create_app
from high_templar.connection import header

api_url = 'http://localhost:8000/api/'


class Settings:
    API_URL = api_url
    FORWARD_IP = 'HTTP_X_REAL_IP'
    CONNECTION_HEADERS = {
        'foo': header.Param('foo').map(str.upper),
    }

    RABBITMQ = {
        'enabled': True,
        'exchange_name': 'hightemplar',
        'host': 'localhost',
        'username': 'rabbitmq',
        'password': 'rabbitmq'
    }


app = create_app(Settings)
