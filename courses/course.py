from enum import Enum

import functools


class TermPeriod(Enum):
    FALL=0,
    SPRING=1,
    SUMMER=2

@functools.total_ordering
class Term():
    def __init__(self, year: int, period: TermPeriod):
        self.year = year
        self.period = period

    def __eq__(self, other):
        return self.year == other.year and self.period == other.period

    def __lt__(self, other):
        if self.year == other.year:
            return self.period.value.__lt__(other.period.value)
        else:
            return self.year.__lt__(other.year)


class Course:
    def __init__(self, subject: str, number: int, term: Term):
        self.subject = subject
        self.number = number
        self.term = term


def format_courses(course_list) -> str:
    pass
    # list of header -> field mappings
    # tabulate_info = ['']
    #
    # header_items = tabulate_info.keys()
    # entry_fields = list(map(lambda header_item: FIELD_MAPPINGS[header_item], header_items))
    #
    # entries = []
    # for assignment in assignment_list:
    #     entry = []
    #     for entry_field in entry_fields:
    #         entry.append(getattr(assignment, entry_field))
    #     entries.append(entry)
    #
    # return tabulate(entries, headers=[], tablefmt='plain')
