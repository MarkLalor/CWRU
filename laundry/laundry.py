import re
from typing import List

import requests
from bs4 import BeautifulSoup, NavigableString
from tabulate import tabulate


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


def get_data(room_id):
    url = 'http://classic.laundryview.com/laundry_room.php?lr=' + room_id
    soup = BeautifulSoup(requests.get(url).text, 'html.parser')

    data = {}

    data['organization'] = soup.select('#monitor-head h1')[0].contents[0]
    data['room'] = soup.select('#monitor-head h2')[0].contents[0]

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

    data['machines'] = {}

    data['machines']['washers'] = parse_machine_column(washers)
    data['machines']['dryers'] = parse_machine_column(dryers)

    return data

def print_laundry(laundry_data, color):
    print(laundry_data['organization'])
    print(laundry_data['room'])
    print()

    def generate_entries(machine_data, kind) -> List[List[str]]:
        from termcolor import colored

        def machine_status(machine):
            result = machine_data[machine]['status']

            if result == 'available' or result.startswith('cycle ended'):
                result = (True, colored(result, 'green') if color else result)
            elif result.startswith('est. time remaining'):
                result = (True, colored(result, 'yellow') if color else result)
            else:
                result = (False, colored(result, 'red') if color else result)

            return result

        entries = []
        for machine_id in machine_data.keys():
            status = machine_status(machine_id)
            entries.append([kind, machine_id, status[1], machine_data[machine_id]['minutes'] if status[0] else '?', '{:.0%}'.format(float(machine_data[machine_id]['progress'])) if status[0] else '?'])

        return entries

    entries = []
    entries += generate_entries(laundry_data['machines']['washers'], kind='washer')
    entries += generate_entries(laundry_data['machines']['dryers'], kind='dryer')

    print(tabulate(entries, headers=['Type', 'ID', 'Status', 'Time', 'Progress'], tablefmt='plain'))


# Command-line entry point:

def laundry(args):
    rooms = list_rooms()

    id = next((v for k, v in rooms.items() if k.lower().replace(" ", "").startswith(args.building.lower().replace(" ", ""))), None)

    if id is None:
        print('Could not find room "%s"' % args.building.lower().replace(" ", ""))
    else:
        parsed = get_data(id)
        print_laundry(parsed, args.c)
