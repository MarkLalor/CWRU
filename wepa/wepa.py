import json

import magic
import os
import requests
from fake_useragent import UserAgent

from cwru import cwru_config

job_data_defaults = {
    'range': 'ALL',
    'start': '1',
    'end': '1',
    'color': 'BLACKANDWHITE',
    'orientation': 'PORTRAIT',
    'duplex': 'false',
    'what': 'SLIDES',
    'handout': 'one',
    'copies': '1',
    'size': '_4x6',
    'scale': 'KeepOriginalAspectRatio',
    'rotate': '1'
}

job_data_requirements = ['fileid', 'range', 'start', 'end', 'color', 'orientation', 'duplex', 'what', 'handout', 'copies', 'extension', 'size', 'scale','rotate']


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
        self.fileids = {}
        self.session = requests.Session()
        self.session.headers.update({'user-agent': UserAgent().chrome})
        self.session.cookies.update({'selectedSchool': 'School'})

        self.__do_login(username, password)

    def __do_login(self, username, password):
        if not self.logged_in:
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
                do_login_response = self.session.get('https://www.wepanow.com/user/do-login', headers={'referer': 'https://www.wepanow.com/login'})

                if do_login_response.status_code == 302 and not do_login_response.headers.get('location') == '/':
                    self.logged_in = True


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

        uploaded_id = response.json()['response']['file_id']

        self.fileids[filename] = uploaded_id

        return response.json()

    # Example return value
    # {"response_type": "success", "response": {"releaseCode": "HEE126", "numPages": 5, "numSheets": 0, "cost": "$0.35",
    #                                           "description": "Cost for Printing ($0.49 per color page)",
    #                                           "dlink": "BASE_PATH/members-area/preview-file?releasecode=HEE126",
    #                                           "type": "success"}, "promo_applied": false, "user_data": null}

    def submit_job(self, data):
        has_all = all(key in data for key in job_data_requirements)

        response = self.session.post('https://www.wepanow.com/members-area/send-to-wepa', headers = {
            'referer': 'https://www.wepanow.com/members-area/'
        }, data=data)

        return response.json()

def generate_submit_data_from_args(fileid, args) -> dict:
    if args.range is None or args.range.lower() == 'all':
        range = 'ALL'
        start = '1'
        end = '1'
    else:
        range_parts = args.range.split('-')

        if len(range_parts) == 2:
            range = 'INCLUSIVERANGE'
            start = range_parts[0]
            end = range_parts[1]
        else:
            print('Invalid range specified (two integers seperated by a hyphen)')
            return {}

    color = 'BLACKANDWHITE' if args.color is None or args.color.lower() == 'blackandwhite' else 'COLOR'
    orientation = 'LANDSCAPE' if args.orientation is None or args.orientation.lower() == 'portrait' else 'PORTRAIT'
    duplex = 'true' if args.duplex is None or args.duplex else 'false'

    copies = '1' if args.quantity is None else str(args.quantity)

    extension = os.path.splitext(args.document)[1][1:]

    return {
        'fileid': fileid,
        'range': range,
        'start': start,
        'end': end,
        'color': color,
        'orientation': orientation,
        'duplex': duplex,
        'what': 'SLIDES',
        'handout': 'one',
        'copies': copies,
        'extension': extension,
        'size': '_4x6',
        'scale': 'KeepOriginalAspectRatio',
        'rotate': '1'
    }


def wepa(args):
    config = cwru_config()
    username = config.get('CWRU', 'username') + '@case.edu'
    password = config.get('CWRU', 'password')

    wepa = Wepa(username, password)

    wepa.do_upload(args.document)
    result = wepa.submit_job(generate_submit_data_from_args(wepa.fileids[args.document], args))

    if result['response_type'] == 'success':
        response = result['response']
        print(args.document + ' successfully uploaded.')
        print(str(response['numPages']) + ' pages (' + response['cost'] + ')')
        print('Release code: ' + response['releaseCode'])
    else:
        print('Failed to submit print request.')
        print(json.dumps(result))
