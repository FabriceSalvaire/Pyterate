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

# Fixme: clean API !!!

# Fixme: These classes do several tasks
#  decode input
#  store data
#  to_rst generate RST
#  to_code

####################################################################################################

__all__ = [
    'Dom',
    'ExecutedNode',
    'MarkdownCellMixin',
    'Node',
    'TextNode',
]

####################################################################################################

import logging
import subprocess

from nbformat import v4 as nbv4

from Pyterate.Tools.MarkupConverter import rest_to_markdown
from .Registry import MarkupRegistry

####################################################################################################

_module_logger = logging.getLogger(__name__)

####################################################################################################

class Node(metaclass=MarkupRegistry):

    """ This class represents a node of lines in the source. """

    MARKUP = None

    _PANDOC_MARKDOWN = 'markdown'

    ##############################################

    @staticmethod
    def indent_lines(lines, indentation=4):

        indentation = ' '*indentation
        # Fixme: strip empty lines
        return '\n'.join([indentation + line.rstrip() for line in lines]) + '\n' # Fixme: if out ???

    ##############################################

    @classmethod
    def indent_output(cls, output, indentation=4):
        return cls.indent_lines(str(output).split('\n'), indentation)

    ##############################################

    @staticmethod
    def directive(name, args=(), flags=(), kwargs={}):

        args_string = ' '.join([str(arg) for arg in args])
        rst = '\n.. {}:: {}\n'.format(name, args_string)
        indentation = ' '*4
        for flag in flags:
            rst += indentation + ':{}:\n'.format(flag)
        for key, value in kwargs.items():
            rst += indentation + ':{}: {}\n'.format(key, value)

        return rst + '\n'

    ##############################################

    @classmethod
    def code_block_directive(cls, lexer):
        return cls.directive('code-block', (lexer,))

    ##############################################

    @classmethod
    def check_command(cls, *command, help='', protect=False):

        # command = list(command)
        # command[0] += '-debug'

        try:
            if protect:
                try:
                    subprocess.check_call(command,
                                          stdout=subprocess.DEVNULL,
                                          stderr=subprocess.DEVNULL,
                                          shell=False)
                except subprocess.CalledProcessError:
                    pass
            else:
                subprocess.check_call(command, stdout=subprocess.DEVNULL, shell=False)
            cls._logger.info('\nFound dependency: %s', command[0])
        except FileNotFoundError:
            cls._logger.error('\nA dependency is missing:\n  %s\n  %s', command[0], help)

    ##############################################

    def __init__(self, document):
        self._document = document # to pass settings ...
        self._lines = []

    ##############################################

    def __repr__(self):
        return '<{}>\n\n'.format(self.__class__.__name__) + str(self)

    ##############################################

    def __str__(self):
        return '\n'.join(self._lines) + '\n'

    ##############################################

    def __bool__(self):
        return bool(self._lines)

    ##############################################

    # def __iter__(self):
    #     return iter(self._lines)

    ##############################################

    def append(self, line):
        self._lines.append(line)

    ##############################################

    def mergable(self, node):
        return self.__class__ is node.__class__

    ##############################################

    def merge(self, node):
        self._lines.extend(node._lines)

    ##############################################

    @property
    def is_executed(self):
        return hasattr(self, 'to_code')

    ##############################################

    @property
    def document(self):
        return self._document

    @property
    def language(self):
        return self._document.language

    ##############################################

    @property
    def opening_format_markup(self):
        return self._document.language.opening_format_markup

    @property
    def closing_format_markup(self):
        return self._document.language.closing_format_markup

    @property
    def escaped_opening_format_markup(self):
        return self._document.language.escaped_opening_format_markup

    @property
    def escaped_closing_format_markup(self):
        return self._document.language.escaped_closing_format_markup

    ##############################################

    @property
    def lexer(self):
        return self.language.lexer

    @property
    def error_lexer(self):
        return self.language.error_lexer

    ##############################################

    def to_rst(self):
        return ''

    ##############################################

    def to_markdown(self):
        return rest_to_markdown(self.to_rst(), self._PANDOC_MARKDOWN)

    ##############################################

    def to_cell(self):
        raise NotImplementedError

####################################################################################################

class ExecutedNode(Node):

    ##############################################

    def __init__(self, document):
        super().__init__(document)
        self.outputs = []

    ##############################################

    def __bool__(self):
        # Fixme: precompute
        for line in self._lines:
            if line.strip():
                return True
        return False

####################################################################################################

class MarkdownCellMixin:

    ##############################################

    def to_cell(self):
        markdown = self.to_markdown()
        return nbv4.new_markdown_cell(markdown)

####################################################################################################

class TextNode(MarkdownCellMixin, Node):

    ##############################################

    def has_format(self):
        for line in self._lines:
            if self.opening_format_markup in line:
                return True
        return False

####################################################################################################

class Dom:

    _logger = _module_logger.getChild('Dom')

    ##############################################

    def __init__(self):
        self._nodes = []

    ##############################################

    def __bool__(self):
        return bool(self._nodes)

    ##############################################

    def __len__(self):
        return len(self._nodes)

    ##############################################

    def __iter__(self):
        return iter(self._nodes)

    ##############################################

    def iter_on_not_empty_node(self):
        for node in self._nodes:
            if node:
                yield node

    ##############################################

    def append(self, node):
        # self._logger.debug(repr(node))
        self._nodes.append(node)

    ##############################################

    @property
    def last_node(self):
        if self._nodes:
            return self._nodes[-1]
        else:
            return None
