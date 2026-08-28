####################################################################################################
#
# Pyterate - Sphinx add-ons to create API documentation for Python projects
# Copyright (C) 2020 Salvaire Fabrice
# SPDX-License-Identifier: GPL-3.0-or-later
#
####################################################################################################

"""Generate a PDF and PNG image for a circuit macros input"""

####################################################################################################

from pathlib import Path
import argparse
import os

#! import ..Doc.CircuitMacrosGenerator as CircuitMacrosGenerator

####################################################################################################

def main():

    argument_parser = argparse.ArgumentParser(
        description='Generate a PDF and PNG image for a circuit macros input.')

    argument_parser.add_argument('m4_path', metavar='M4_PATH',
                                 help='m4 path')

    argument_parser.add_argument('dst_path', metavar='DST_PATH',
                                 help='destination path')

    args = argument_parser.parse_args()

    CircuitMacrosGenerator.generate(Path(args.m4_path).resolve(), Path(args.dst_path).resolve())
