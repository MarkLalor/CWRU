import json

import re
import requests
from bs4 import BeautifulSoup, NavigableString


def no_strings(contents):
    return [x for x in contents if not isinstance(x, NavigableString)]

def down_first(element, times):
    current_contents = element.contents
    for _ in range(times - 1):
        current_contents = next(item for item in current_contents if not isinstance(item, NavigableString)).contents
    return current_contents[0]


def list_rooms():
    url = 'http://classic.laundryview.com/lvs.php?s=4061'
    soup = BeautifulSoup(requests.get(url).text, 'html.parser')

    def extract_name(element):
        return element.contents[0].strip().upper()

    def extract_id(element):
        return element['href'].split("?lr=", 1)[1]

    return {extract_name(a): extract_id(a) for a in soup.select('#campus1 a')}


def get_minutes(status):
    return


def get_info(room_id):
    url = 'http://classic.laundryview.com/laundry_room.php?lr=' + room_id
    soup = BeautifulSoup(requests.get(url).text, 'html.parser')

    info = {}

    info['organization'] = soup.select('#monitor-head h1')[0].contents[0]
    info['room'] = soup.select('#monitor-head h2')[0].contents[0]

    washers = soup.select('#classic_monitor > table > tr > td[align="left"] > table > tr')
    dryers  = soup.select('#classic_monitor > table > tr > td[align="right"] > table > tr')


    def parse_machine_column(rows):
        # the relevant info per machine is actually stored in two rows
        machine = {}

        def add_machine_info(id_data, progress_data, status_data):
            id = down_first(id_data, times=2).strip()
            status = down_first(status_data, times=3).strip()
            progress = int(down_first(progress_data, times=7)['width'])/240 # 240 is the max width of the progress bar

            machine[id] = {
                'status': status,
                'minutes': int(re.search('\d+', status).group()) if 'est. time remaining' in status else 0,
                'progress': progress
            }

        while rows:
            row1 = no_strings(rows.pop(0).contents)
            id_data = row1[1]
            progress_data = row1[2]
            row2 = no_strings(rows.pop(0).contents)
            status_data = row2[0]

            add_machine_info(id_data, progress_data, status_data)

        return machine


    info['machines'] = {}

    info['machines']['washers'] = parse_machine_column(washers)
    info['machines']['dryers'] = parse_machine_column(dryers)

    return info


def print_laundry(laundry_data):
    print(laundry_data['organization'])
    print(laundry_data['room'])
    print()

    def print_machine(machine_data, kind):
        pass

    print_machine(laundry_data['washers'])
    print_machine(laundry_data['dryers'], kind='dryer')


def laundry(args):
    rooms = list_rooms()

    id = next(v for k, v in rooms.items() if k.startswith(args.building.upper()))

    if id is None:
        print('no matches :/')
    else:
        parsed = get_info(id)
        print_laundry(parsed)
