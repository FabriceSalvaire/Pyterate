####################################################################################################
#
# Pyterate - Sphinx add-ons to create API documentation for Python projects
# Copyright (C) 2014 Fabrice Salvaire
# SPDX-License-Identifier: GPL-3.0-or-later
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

    def convert_markup(*args, **kwargs) -> str:
        return _convert_text(args[0], kwargs['to_format'], format=kwargs['from_format'])
except ImportError:
    _module_logger.warning('pypandoc is not installed')

    def convert_markup(*args, **kwargs) -> str:
        return 'ERROR: pypandoc is not installed'

####################################################################################################

def markdown_to_rest(md_text: str, markdown_format: str = 'markdown') -> str:
    rest_text = convert_markup(md_text, from_format=markdown_format, to_format='rst')
    return rest_text

####################################################################################################

def rest_to_markdown(rest_text: str, markdown_format: str = 'markdown') -> str:
    # Fixme: use markdown_strict+tex_math_dollars
    # _module_logger.info(rest_text)
    _ = convert_markup(rest_text, from_format='rst', to_format=markdown_format)
    md_text = ''
    for line in _.splitlines():
        if not line.startswith(':::'):
            md_text += line + '\n'
    return md_text

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
