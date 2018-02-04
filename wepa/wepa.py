import json

import magic
import os
import requests
from fake_useragent import UserAgent

def pretty_print_POST(req):
    """
    At this point it is completely built and ready
    to be fired; it is "prepared".

    However pay attention at the formatting used in
    this function because it is programmed to be pretty
    printed and may differ from the actual request.
    """
    print('{}\n{}\n{}\n\n{}'.format(
        '-----------START-----------',
        req.method + ' ' + req.url,
        '\n'.join('{}: {}'.format(k, v) for k, v in req.headers.items()),
        req.body,
    ))

class Wepa(object):
    MAX_FILE_SIZE = 20971520

    def __init__(self, username, password):
        self.logged_in = False
        self.session = requests.Session()
        self.session.headers.update({'user-agent': UserAgent().chrome})
        self.session.cookies.update({'selectedSchool': 'School'})

        self.__do_login(username, password)

    def __do_login(self, username, password):
        self.session.get('https://www.wepanow.com/login')

        # These are just based on what wepanow.com actually uses...
        # Obviously it would make sense to supply a correct school/timezone, but they don't seem to lol.
        response = self.session.get('https://www.wepanow.com/user/check-login', params={
            'login_school': '',
            'login_username': username,
            'login_password': password,
            'timezone': 'America/New_York'
        }, headers={
            'referer': 'https://www.wepanow.com/login',
            'x-requested-with': 'XMLHttpRequest'
        })

        if response.json()['type'] == 'valid':
            self.session.get('https://www.wepanow.com/user/do-login', headers={'referer': 'https://www.wepanow.com/login'})


    def do_upload(self, filename) -> str:
        # Use python-magic library to determine MIME type
        content_type = magic.Magic(mime=True).from_file(filename)

        response = self.session.post('https://www.wepanow.com/members-area/do-upload',
                                headers={
                                    'origin': 'https://www.wepanow.com',
                                    'referer': 'https://www.wepanow.com/members-area/',
                                    'X-Requested-With': 'XMLHttpRequest'},
                                data={'MAX_FILE_SIZE': self.MAX_FILE_SIZE},
                                files={'mapn-file': (os.path.basename(filename), open(filename, 'rb'), content_type)})

        return response.json()['response']['file_id']

    # Example return value
    # {"response_type": "success", "response": {"releaseCode": "HEE126", "numPages": 5, "numSheets": 0, "cost": "$0.35",
    #                                           "description": "Cost for Printing ($0.49 per color page)",
    #                                           "dlink": "BASE_PATH/members-area/preview-file?releasecode=HEE126",
    #                                           "type": "success"}, "promo_applied": false, "user_data": null}

    def do_submit(self, fileid):
        response = self.session.post('https://www.wepanow.com/members-area/send-to-wepa', headers = {
            'referer': 'https://www.wepanow.com/members-area/'
        }, data = {
            'fileid': fileid,
            'range': 'ALL',
            'start': '1',
            'end': '1',
            'color': 'BLACKANDWHITE',
            'orientation': 'PORTRAIT',
            'duplex': 'false',
            'what': 'SLIDES',
            'handout': 'one',
            'copies': '1',
            'extension': 'pdf',
            'size': '_4x6',
            'scale': 'KeepOriginalAspectRatio',
            'rotate': '1'
        })

        return response.json()


def wepa(args):
    filepath = args.document

    wepa = Wepa('username', 'password')

    fileid = wepa.do_upload(filepath)

    result = wepa.do_submit(fileid)

    if result['response_type'] == 'success':
        response = result['response']
        print(filepath + ' successfully uploaded.')
        print(str(response['numPages']) + ' pages (' + response['cost'] + ')')
        print('Release code: ' + response['releaseCode'])
    else:
        print('Failed to submit print request.')
        print(json.dumps(result))
