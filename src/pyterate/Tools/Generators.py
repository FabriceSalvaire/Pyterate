####################################################################################################
#
# Pyterate - Sphinx add-ons to create API documentation for Python projects
# Copyright (C) 2014 Fabrice Salvaire
# SPDX-License-Identifier: GPL-3.0-or-later
#
####################################################################################################

""" This module implements generators.
"""

####################################################################################################

def sublist_accumulator_iterator(iterable):

    # used to implement os.makedirs

    """From a list (1, 2, 3, ...) this generator yields (), (1,), (1, 2), (1, 2, 3), ..."""

    for i in range(len(iterable) +1):
        yield iterable[:i]
