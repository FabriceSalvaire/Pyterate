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

"""Helpers to convert markup languages.

* Pandoc a universal document converter https://pandoc.org

"""

####################################################################################################

__all__ = [
    # 'convert_markup',
    'rest_to_markdown',
    'markdown_to_rest',
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

####################################################################################################

def markdown_to_rest(md_text, markdown_format='markdown'):
    rest_text = convert_markup(md_text, from_format=markdown_format, to_format='rst')
    return rest_text

####################################################################################################

def rest_to_markdown(rest_text, markdown_format='markdown'):

    # Fixme: use markdown_strict+tex_math_dollars

    # markdown:
    #    add ::: line
    #    LaTeX ok
    #    table not ok
    # markdown_strict:
    #     add \ to LaTeX
    #     table ok
    # markdown_strict+tex_math_dollars:
    # gfm:
    #    add <div> ... </div>
    #     \[ latex ... \]

    # _module_logger.info(rest_text)
    _ = convert_markup(rest_text, from_format='rst', to_format=markdown_format)

    md_text = ''
    for line in _.splitlines():
        if not line.startswith(':::'):
            md_text += line + '\n'

    return md_text
