from tabulate import tabulate

class Assignment:
    def __init__(self, date=None, points=None, total=None, name=None):
        self.date = date
        self.points = points
        self.total = total
        self.name = name
        

FIELD_MAPPINGS = {
    'Date': 'date',
    'Points': 'points',
    'Total': 'total',
    'Name': 'name'
}

def format_assignments(assignment_list) -> str:
    # list of header -> field mappings
    tabulate_info = FIELD_MAPPINGS

    header_items = tabulate_info.keys()
    entry_fields = list(map(lambda header_item: FIELD_MAPPINGS[header_item], header_items))

    entries = []
    for assignment in assignment_list:
        entry = []
        for entry_field in entry_fields:
            entry.append(getattr(assignment, entry_field))
        entries.append(entry)

    return tabulate(entries, headers=[], tablefmt='plain')