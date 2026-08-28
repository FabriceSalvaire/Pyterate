####################################################################################################
#
# Pyterate - Sphinx add-ons to create API documentation for Python projects
# Copyright (C) 2014 Fabrice Salvaire
# SPDX-License-Identifier: GPL-3.0-or-later
#
####################################################################################################

__all__ = ['rst_rule_title']

####################################################################################################

def rst_rule_title(title: str, character: str = '=') -> str:
    return character*(len(str(title)) + 2)
