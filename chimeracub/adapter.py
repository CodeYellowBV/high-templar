import requests


class Adapter:
    '''
    Translates incoming requests from the django app to hub actions
    and vice versa.
    '''

    def __init__(self, app):
        self.app = app
        self.base_url = 'http://{}:{}'.format(app.config['DJANGO_APP_URL'], app.config['DJANGO_APP_PORT'])

    def check_auth(self, socket):
        ws = socket.ws
        headers = {
            'cookie': ws.environ['HTTP_COOKIE'],
            'host': ws.environ['HTTP_HOST'],
            'user-agent': ws.environ['HTTP_USER_AGENT']
        }
        res = requests.get('{}/api/bootstrap/'.format(self.base_url), headers=headers)

        if res.status_code != 200:
            return False

        socket.parse_user(res.json()['user'])
        return True
