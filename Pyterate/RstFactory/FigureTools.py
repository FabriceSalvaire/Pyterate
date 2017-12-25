####################################################################################################
#
# Pyterate - Sphinx add-ons to create API documentation for Python projects
# Copyright (C) 2014 Fabrice Salvaire
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

####################################################################################################

__all__ = [
    'save_figure',
    'export_value',
]

####################################################################################################

import json
import logging

import numpy

from ..Tools.Path import file_extension

####################################################################################################

_module_logger = logging.getLogger(__name__)

####################################################################################################

def save_figure(figure, figure_path):

    """ This function is called from document to save a figure. """

    figure_format = file_extension(figure_path)[1:] # foo.png -> png
    _module_logger.info("\nSave figure " + figure_path)
    figure.savefig(
        figure_path,
        format=figure_format,
        dpi=150,
        orientation='landscape', papertype='a4',
        transparent=True, frameon=False,
    )


####################################################################################################

def export_value(value):

    if isinstance(value, numpy.ndarray):
        value = value.tolist()

    # Can export basic type: str, int, float
    # as well as tuple, list or dict of basic type

    return json.dumps(value)
