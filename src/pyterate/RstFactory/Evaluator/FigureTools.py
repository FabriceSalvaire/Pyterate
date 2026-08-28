####################################################################################################
#
# Pyterate - Sphinx add-ons to create API documentation for Python projects
# Copyright (C) 2014 Fabrice Salvaire
# SPDX-License-Identifier: GPL-3.0-or-later
#
####################################################################################################

"""Helpers for figures.

Theses functions are executed in a Jupyter kernel.

"""

####################################################################################################

__all__ = [
    'save_figure',
    'export_value',
]

####################################################################################################

from pathlib import Path
import json
import logging

import numpy

####################################################################################################

_module_logger = logging.getLogger(__name__)

####################################################################################################

def save_figure(figure, figure_path):
    """ This function is called from document to save a figure. """
    figure_format = Path(figure_path).suffix[1:] # remove .
    _module_logger.info("\nSave figure " + figure_path)
    # https://matplotlib.org/stable/api/figure_api.html?highlight=savefig#matplotlib.figure.Figure.savefig
    figure.savefig(
        figure_path,
        format=figure_format,
        dpi=150,
        orientation='landscape',
        # papertype='a4',
        transparent=True, facecolor=None,
    )

####################################################################################################

def export_value(value):
    if isinstance(value, numpy.ndarray):
        value = value.tolist()
    # Can export basic type: str, int, float
    # as well as tuple, list or dict of basic type
    return json.dumps(value)
