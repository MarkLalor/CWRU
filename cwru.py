#!/usr/bin/env python
import argparse
import configparser
import logging
import os
from pathlib import Path

import re

from laundry import laundry
from wepa import wepa


def cwru_dir() -> Path:
    return Path(os.getenv('CWRU_HOME', os.path.join(os.environ['HOME'], 'cwru')))


# Only lazy-load config file once when running the program.
config = None


def cwru_config() -> configparser.ConfigParser:
    global config
    if config is None:
        config = configparser.ConfigParser()
        config_filepath = cwru_dir().joinpath('config.ini')
        config.read(config_filepath)

    return config


def main():
    logger = logging.getLogger(__name__)
    logger.addHandler(logging.StreamHandler())
    logger.setLevel(logging.DEBUG)
    logger.info(cwru_dir())

    # Log some basic info for debugging purposes

    # Handle subcommand delegation
    parser = argparse.ArgumentParser(description='This is the top-level description')
    subparsers = parser.add_subparsers(help='subparsers help')

    parser.add_argument('-c', action='store_false')

    laundry_parser = subparsers.add_parser('laundry')
    laundry_parser.add_argument('building')
    laundry_parser.set_defaults(func=laundry.laundry)

    # ================== WEPA ==================

    wepa_parser = subparsers.add_parser('wepa')
    wepa_parser.set_defaults(func=wepa.wepa)

    wepa_parser.add_argument('document', help='Path to document to upload.')

    wepa_parser.add_argument('-q', '--quantity', type=int, help='Number of copies to print.')
    wepa_parser.add_argument('-d', '--duplex', action='store_true', help='Print copies on both sides of paper.')
    wepa_parser.add_argument('-c', '--color', choices=['greyscale', 'color'], help='Print in greyscale or color.')

    pat = re.compile(r"^(ALL|[0-9]+\-[0-9]+)$")
    def range_regex_type(s):
        if not pat.match(s, re.IGNORECASE):
            raise argparse.ArgumentTypeError
        return s

    wepa_parser.add_argument('-r', '--range', type=range_regex_type, help='Range of pages to print.')
    wepa_parser.add_argument('-o', '--orientation', choices=['portrait', 'landscape'], help='Print in portrait or landscape orientation')

    args = parser.parse_args()
    args.func(args)

    # token = cwru_dir().joinpath('canvas', 'token').read_text()



if __name__ == '__main__':
    main()