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

"""Helper to convert markup languages.

* Pandoc a universal document converter https://pandoc.org

"""

####################################################################################################

__all__ = [
    'convert_markup',
]

####################################################################################################

import logging

####################################################################################################

_module_logger = logging.getLogger(__name__)

####################################################################################################

try:
    from pypandoc import convert_text as _convert_text
    def convert_markup(*args, **kwargs):
        return _convert_text(args[0], kwargs['to_format'], format=kwargs['from_format'])
except ImportError:
    _module_logger.warning('pypandoc is not installed')
    def convert_markup(*args, **kwargs):
        return 'ERROR: pypandoc is not installed'
