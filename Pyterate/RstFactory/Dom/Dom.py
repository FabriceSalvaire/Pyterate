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
#   decode input
#   store data
#   to_rst generate RST
#   to_code
# Fixme: cyclic dependency

####################################################################################################

__all__ = [
    'Dom',
    'ExecutedNode',
    'MarkdownCellMixin',
    'MystMixin',
    'Node',
    'TextNode',
]

####################################################################################################

import logging
import os
import subprocess
from typing import TYPE_CHECKING, Iterable

# https://nbformat.readthedocs.io/en/latest/api.html#module-nbformat.v4
from nbformat import v4 as nbv4
from nbformat import NotebookNode

from Pyterate.Tools.MarkupConverter import rest_to_markdown
from .Registry import MarkupRegistry

if TYPE_CHECKING:
    from ..Document import Document
    from ..Settings import Language

####################################################################################################

NEWLINE = os.linesep

_module_logger = logging.getLogger(__name__)

####################################################################################################

class Node(metaclass=MarkupRegistry):

    """ This class represents a node of lines in the source. """

    MARKUP = None

    _PANDOC_MARKDOWN = 'markdown'
    RST_INDENTATION = 4

    ##############################################

    @classmethod
    def indentation(cls, use_myst: bool) -> int:
        if use_myst:
            return 0
        else:
            return cls.RST_INDENTATION

    ##############################################

    @staticmethod
    def indent_lines(lines: list[str], indentation: int = 4) -> str:
        indentation = ' '*indentation
        # Fixme: if out ???
        # strip empty lines at the begining and end
        first_line = 0
        last_line = len(lines)
        for first_line, line in enumerate(lines):
            if line:
                break
        for i, line in enumerate(reversed(lines)):
            if line:
                last_line -= i
                break
        return NEWLINE.join([indentation + _.rstrip() for _ in lines[first_line:last_line]]) + NEWLINE

    ##############################################

    @classmethod
    def indent_output(cls, output, indentation: int = 4) -> str:
        return cls.indent_lines(str(output).split(NEWLINE), indentation)

    ##############################################

    @staticmethod
    def directive(
        name: str,
        args: list = (),
        flags: list = (),
        kwargs: dict = {},
        use_myst: bool = False,
    ) -> str:
        args_string = ' '.join([str(_) for _ in args])
        if use_myst:
            rst = f'{NEWLINE}```{{{name}}} {args_string}{NEWLINE}'
            indentation = ''
        else:
            rst = f'{NEWLINE}.. {name}:: {args_string}{NEWLINE}'
            indentation = ' '*4
        for _ in flags:
            rst += f'{indentation}:{_}:{NEWLINE}'
        for key, value in kwargs.items():
            rst += f'{indentation}:{key}: {value}{NEWLINE}'
        rst += NEWLINE
        return rst

    # @staticmethod
    # def rst_directive(name, args=(), flags=(), kwargs={}) -> str:
    #     return Node.directive(name, args, kwargs, use_myst=False)

    @staticmethod
    def myst_directive(
        name: str,
        args: list = (),
        flags: list = (),
        kwargs: dict = {},
    ) -> str:
        return Node.directive(name, args, kwargs, use_myst=True)

    # Fixme:
    @staticmethod
    def close_directive(
        use_myst: bool = False,
    ) -> str:
        if use_myst:
            return '```' + NEWLINE
        else:
            return ''

    ##############################################

    @classmethod
    def code_block_directive(
        cls,
        lexer: str,
        use_myst: bool = False,
    ) -> str:
        return cls.directive('code-block', args=(lexer,), use_myst=use_myst)

    ##############################################

    @classmethod
    def check_command(cls, *command, help='', protect=False) -> None:
        # command = list(command)
        # command[0] += '-debug'
        try:
            if protect:
                try:
                    subprocess.check_call(
                        command,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                        shell=False,
                    )
                except subprocess.CalledProcessError:
                    pass
            else:
                subprocess.check_call(command, stdout=subprocess.DEVNULL, shell=False)
            cls._logger.info('\nFound dependency: %s', command[0])
        except FileNotFoundError:
            cls._logger.error('\nA dependency is missing:\n  %s\n  %s', command[0], help)

    ##############################################

    def __init__(self, document: 'Document') -> None:
        self._document = document   # to pass settings ...
        self._lines = []

    ##############################################

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__}>{NEWLINE}{NEWLINE}{self}'

    ##############################################

    def __str__(self) -> str:
        return NEWLINE.join(self._lines) + NEWLINE

    ##############################################

    def __bool__(self) -> bool:
        return bool(self._lines)

    ##############################################

    # def __iter__(self):
    #     return iter(self._lines)

    ##############################################

    def append(self, line: str) -> None:
        self._lines.append(line)

    ##############################################

    def mergable(self, node: 'Node') -> bool:
        return self.__class__ is node.__class__

    ##############################################

    def merge(self, node: 'Node') -> None:
        self._lines.extend(node._lines)

    ##############################################

    @property
    def is_executed(self) -> bool:
        return hasattr(self, 'to_code')

    ##############################################

    @property
    def document(self) -> 'Document':
        return self._document

    @property
    def language(self) -> 'Language':
        return self._document.language

    ##############################################

    @property
    def opening_format_markup(self) -> str:
        return self._document.language.opening_format_markup

    @property
    def closing_format_markup(self) -> str:
        return self._document.language.closing_format_markup

    @property
    def escaped_opening_format_markup(self) -> str:
        return self._document.language.escaped_opening_format_markup

    @property
    def escaped_closing_format_markup(self) -> str:
        return self._document.language.escaped_closing_format_markup

    ##############################################

    @property
    def lexer(self) -> str:
        return self.language.lexer

    @property
    def error_lexer(self) -> str:
        return self.language.error_lexer

    ##############################################

    def to_rst(self) -> str:
        return ''

    ##############################################

    def to_markdown(self) -> str:
        return rest_to_markdown(self.to_rst(), self._PANDOC_MARKDOWN)

    ##############################################

    def to_myst(self) -> str:
        # return ''
        # return self.to_markdown()
        return f'{self.__class__} NotImplementedError'

    ##############################################

    def to_cell(self) -> NotebookNode:
        raise NotImplementedError

####################################################################################################

class ExecutedNode(Node):

    ##############################################

    def __init__(self, document: 'Document') -> None:
        super().__init__(document)
        self.outputs = []

    ##############################################

    def __bool__(self) -> bool:
        # Fixme: precompute
        for _ in self._lines:
            if _.strip():
                return True
        return False

####################################################################################################

class MarkdownCellMixin:

    ##############################################

    def to_cell(self) -> NotebookNode:
        markdown = self.to_markdown()
        return nbv4.new_markdown_cell(markdown)

####################################################################################################

class MystMixin:

    def to_rst(self) -> str:
        return self._to_rst(use_myst=False)

    def to_myst(self) -> str:
        return self._to_rst(use_myst=True)

####################################################################################################

class TextNode(MarkdownCellMixin, Node):

    ##############################################

    def has_format(self) -> bool:
        for _ in self._lines:
            if self.opening_format_markup in _:
                return True
        return False

####################################################################################################

class Dom:

    _logger = _module_logger.getChild('Dom')

    ##############################################

    def __init__(self) -> None:
        self._nodes = []

    ##############################################

    def __bool__(self) -> bool:
        return bool(self._nodes)

    ##############################################

    def __len__(self) -> int:
        return len(self._nodes)

    ##############################################

    def __iter__(self) -> Iterable[Node]:
        return iter(self._nodes)

    ##############################################

    def iter_on_not_empty_node(self) -> Iterable[Node]:
        for _ in self._nodes:
            if _:
                yield _

    ##############################################

    def append(self, node: Node) -> None:
        # self._logger.debug(repr(node))
        self._nodes.append(node)

    ##############################################

    @property
    def last_node(self) -> Node:
        if self._nodes:
            return self._nodes[-1]
        else:
            return None
