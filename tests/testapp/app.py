#!/usr/bin/env python3
from high_templar.main import create_app

django_app_url = 'localhost'
django_app_port = 8000


class Settings:
    DJANGO_APP_URL = django_app_url
    DJANGO_APP_PORT = django_app_port


app = create_app(Settings)
