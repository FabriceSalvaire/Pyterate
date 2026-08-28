####################################################################################################
#
# Pyterate - Sphinx add-ons to create API documentation for Python projects
# Copyright (C) 2017 Salvaire Fabrice
# SPDX-License-Identifier: GPL-3.0-or-later
#
####################################################################################################

####################################################################################################

import Pyterate.Logging.Logging as Logging
logger = Logging.setup_logging()

####################################################################################################

from pathlib import Path
import argparse
import os

import Pyterate
from Pyterate.ApiRstFactory import ApiRstFactory

####################################################################################################

def main():

    parser = argparse.ArgumentParser(description='Generate API Documentation')

    parser.add_argument('module_path', metavar='ModulePath',
                        help='module path')

    parser.add_argument('--rst-api-path',
                        default=Path().joinpath('doc', 'sphinx', 'source', 'api'),
                        help='rst API path')

    parser.add_argument('--exclude', nargs='+',
                        help='rst API path')

    parser.add_argument('--version',
                        action='store_true', default=False,
                        help="Show version")

    args = parser.parse_args()


    if args.version:
        Pyterate.show_version()
        exit(0)

    if args.exclude:
        excluded_directory = args.exclude
    else:
        excluded_directory = ()

    rst_factory = ApiRstFactory(args.module_path, args.rst_api_path, excluded_directory)
    # Fixme: API ???
