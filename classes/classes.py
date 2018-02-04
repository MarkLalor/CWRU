# Command-line entry point:
import re

from cwru import cwru_dir


def list_classes():
    return list(cwru_dir().joinpath('classes').iterdir())

def classes(args):
    all_classes = list_classes()
    id = args.id.lower()

    def is_match(candidate, input):
        return all(string in candidate.lower() for string in [x.trim().lower() for x in re.split('(\d+)', input)])

    matches = [x for x in all_classes if is_match(x, id)]

    print(matches)
