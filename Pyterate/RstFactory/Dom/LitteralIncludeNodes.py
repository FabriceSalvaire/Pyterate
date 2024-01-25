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

from .Dom import Node

####################################################################################################

NEWLINE = os.linesep

# _module_logger = logging.getLogger(__name__)

####################################################################################################

class LiteralIncludeNode(Node):

    """This class represents a literal include block."""

    COMMAND = 'literal_include'

    ##############################################

    def __init__(self, document, include_path) -> None:
        super().__init__(document)
        self._include_filename = document.symlink_source(Path(include_path))
        self._include_path = document.topic.join_path(include_path)

    ##############################################

    def to_rst(self):
        return self.directive(
            'literalinclude',
            args=(self._include_filename,),
        )

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

    def to_rst(self):
        return self.directive(
            'getthecode',
            args=(self._include_filename,),
            kwargs=dict(language=self.lexer),
        )
