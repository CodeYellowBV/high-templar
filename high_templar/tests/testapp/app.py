#!/usr/bin/env python3
from high_templar.main import create_app

api_url = 'http://localhost:8000/api/'


class Settings:
    API_URL = api_url


app = create_app(Settings)
