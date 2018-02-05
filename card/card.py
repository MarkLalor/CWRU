from fake_useragent import UserAgent
from requests import Session

from cwru import cwru_config


class Card(object):

    def __init__(self, username, password):
        self.logged_in = False
        self.session = Session()
        self.session.headers.update({'user-agent': UserAgent().chrome})

        self.__do_login(username, password)

    def __do_login(self, username, password):
        if not self.logged_in:
            pass


def card(args):
    config = cwru_config()
    username = config.get('CWRU', 'username')
    password = config.get('CWRU', 'password')

    card = Card(username, password)