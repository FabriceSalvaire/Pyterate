####################################################################################################
#
# Pyterate - Sphinx add-ons to create API documentation for Python projects
# Copyright (C) 2014 Fabrice Salvaire
# SPDX-License-Identifier: GPL-3.0-or-later
#
####################################################################################################

"""This module contains literal include nodes.

"""

####################################################################################################

__all__ = [
    'LiteralIncludeNode',
    'GetthecodeNode',
]

####################################################################################################

# import logging
import os
from pathlib import Path

from .Dom import Node, MystMixin

####################################################################################################

NEWLINE = os.linesep

# _module_logger = logging.getLogger(__name__)

####################################################################################################

class LiteralIncludeNode(MystMixin, Node):

    """This class represents a literal include block."""

    COMMAND = 'literal_include'

    ##############################################

    def __init__(self, document, include_path) -> None:
        super().__init__(document)
        self._include_filename = document.symlink_source(Path(include_path))
        self._include_path = document.topic.join_path(include_path)

    ##############################################

    def _to_rst(self, use_myst: bool = False) -> str:
        rst = self.directive(
            'literalinclude',
            args=(self._include_filename,),
            use_myst=use_myst,
        )
        rst += self.close_directive(use_myst)
        return rst

    ##############################################

    def to_markdown(self) -> str:
        text = '```\n'
        with open(self._include_path) as fh:
            text += fh.read()
        text += '```\n'
        return text

####################################################################################################

class GetthecodeNode(LiteralIncludeNode):

    """This class represents a literal include block."""

    COMMAND = 'getthecode'

    ##############################################

    def _to_rst(self, use_myst: bool = False) -> str:
        rst = self.directive(
            'getthecode',
            args=(self._include_filename,),
            kwargs=dict(language=self.lexer),
            use_myst=use_myst,
        )
        rst += self.close_directive(use_myst)
        return rst
