#!/usr/bin/env python
import argparse
import logging
import os
from pathlib import Path
from cwrucli.assignments.assignment import Assignment, format_assignments
from cwrucli.canvas.canvas import Canvas
from cwrucli.laundry.laundry import list_rooms, laundry


def cwru_dir() -> Path:
    return Path(os.getenv('CWRU_HOME', os.path.join(os.environ['HOME'], 'cwru')))

def main():
    logger = logging.getLogger(__name__)
    logger.addHandler(logging.StreamHandler())
    logger.setLevel(logging.DEBUG)
    logger.info(cwru_dir())

    # Log some basic info for debugging purposes

    # Handle subcommand delegation
    parser = argparse.ArgumentParser(description='This is the top-level description')
    subparsers = parser.add_subparsers(help='subparsers help')

    laundry_parser = subparsers.add_parser('laundry')
    laundry_parser.add_argument('building')
    laundry_parser.set_defaults(func=laundry)

    args = parser.parse_args()
    args.func(args)

    # token = cwru_dir().joinpath('canvas', 'token').read_text()

    #
    # a1 = Assignment(name='Test 1', points=43, total=50, date='11/5/17')
    # a2 = Assignment(name='Test 2', points=12, total=50, date='11/18/17')
    # a3 = Assignment(name='Test 3', points=100, total=100, date='12/1/17')
    #
    # assignments = [a1, a2, a3]
    #
    # print(format_assignments(assignments))

    # canvas = Canvas('https://canvas.case.edu', token)
    # print(canvas.classes())


if __name__ == '__main__':
    main()