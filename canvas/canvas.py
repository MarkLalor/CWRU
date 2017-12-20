import json

import requests


class Canvas:
    def __init__(self, host, token):
        self.host = host
        self.token = token

    def url(self, path):
        return self.host + path

    def auth_header(self):
        return {'Authorization': 'Bearer ' + self.token}

    def courses(self):
        return requests.get(self.url('/api/v1/courses'), headers=self.auth_header()).json();
