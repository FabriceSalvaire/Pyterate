####################################################################################################
#
# Pyterate - Sphinx add-ons to create API documentation for Python projects
# Copyright (C) 2020 Salvaire Fabrice
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
####################################################################################################

"""Generate a PDF and PNG image for a circuit macros input"""

####################################################################################################

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

    CircuitMacrosGenerator.generate(os.path.realpath(args.m4_path),
                                    os.path.realpath(args.dst_path))
