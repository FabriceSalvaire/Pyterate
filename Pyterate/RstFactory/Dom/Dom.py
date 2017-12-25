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
    'Chunk',
    'Dom',
    'ExecutedChunk',
    'TextChunk',
]

####################################################################################################

import logging
import os

from ..MarkupConverter import convert_markup
from .Registry import MarkupRegistry

####################################################################################################

_module_logger = logging.getLogger(__name__)

####################################################################################################

# Fixme: -> Node ???

class Chunk(metaclass=MarkupRegistry):

    """ This class represents a chunk of lines in the source. """

    MARKUP = None

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

    def mergable(self, chunk):
        return self.__class__ is chunk.__class__

    ##############################################

    def merge(self, chunk):
        self._lines.extend(chunk._lines)

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

        return convert_markup(self.to_rst(), from_format='rst', to_format='md')

####################################################################################################

class ExecutedChunk(Chunk):

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

class TextChunk(Chunk):

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

        self._chunks = []

    ##############################################

    def __bool__(self):
        return bool(self._chunks)

    ##############################################

    def __len__(self):
        return len(self._chunks)

    ##############################################

    def __iter__(self):
        return iter(self._chunks)

    ##############################################

    def iter_on_not_empty_chunk(self):

        for chunk in self._chunks:
            if chunk:
                yield chunk

    ##############################################

    def iter_on_code_chunks(self):

        for chunk in self._chunks:
            if chunk.is_executed:
                yield chunk

    ##############################################

    def append(self, chunk):

        # self._logger.debug(repr(chunk))
        self._chunks.append(chunk)

    ##############################################

    @property
    def last_chunk(self):

        if self._chunks:
            return self._chunks[-1]
        else:
            return None
