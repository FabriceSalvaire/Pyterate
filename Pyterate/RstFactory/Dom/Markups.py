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

####################################################################################################

__all__ = [
    'CodeChunk',
    'CommentChunk',
    'FigureChunk',
    'GuardedCodeChunk',
    'HiddenCodeChunk',
    'InteractiveCodeChunk',
    'LiteralChunk',
    'MarkdownChunk',
    'OutputChunk',
    'RstChunk',
]

####################################################################################################

import logging

from ..MarkupConverter import convert_markup
from .Dom import Chunk, ExecutedChunk, TextChunk

####################################################################################################

_module_logger = logging.getLogger(__name__)

####################################################################################################

class CommentChunk(Chunk):
    MARKUP = '?'

####################################################################################################

class FigureChunk(Chunk):
    MARKUP = 'f'

####################################################################################################

class RstChunk(TextChunk):

    """ This class represents a RST content. """

    MARKUP = 'r'

    ##############################################

    def to_rst(self):
        return str(self)

    ##############################################

    def to_rst_format_chunk(self):

        return RstFormatChunk(self)

####################################################################################################

class LiteralChunk(Chunk):

    """ This class represents a literal block. """

    MARKUP = 'l'

    ##############################################

    def to_rst(self):

        if bool(self):
            source = self.indent_lines(self._lines)
            # rst = self.directive('class', args=('literal-chunk',)) # Don't work !
            return self.code_block_directive('py') + source + '\n'
        else:
            return ''

####################################################################################################

class MarkdownChunk(TextChunk):

    """ This class represents a RST content. """

    MARKUP = 'm'

    ##############################################

    def to_markdown(self):
        return str(self)

    ##############################################

    def to_rst(self):
        return convert_markup(self.to_markdown(), from_format='md', to_format='rst')

    ##############################################

    # def to_rst_format_chunk(self):
    #
    #     return RstFormatChunk(self)

####################################################################################################

class RstFormatChunk(ExecutedChunk):

    ##############################################

    def __init__(self, rst_chunk):

        super().__init__(rst_chunk.document)

        self._lines = rst_chunk._lines

    ##############################################

    def to_rst(self):

        # Fixmes: more than one output

        return str(self.outputs[0]) + '\n'

    ##############################################

    def to_code(self):

        rst = '\n'.join(self._lines)
        rst = rst.replace('{', '{{') # to escape them
        rst = rst.replace('}', '}}')
        rst = rst.replace(self.opening_format_markup, '{')
        rst = rst.replace(self.closing_format_markup, '}')
        rst = rst.replace(self.escaped_opening_format_markup, self.opening_format_markup)
        rst = rst.replace(self.escaped_closing_format_markup, self.closing_format_markup)

        return 'print(r"""' + rst + '""".format(**locals()))\n'

####################################################################################################

class CodeChunk(ExecutedChunk):

    """ This class represents a code block. """

    MARKUP = 'code' # fake markup

    ##############################################

    def to_rst(self):

        if bool(self):
            # Fixme: if previous is hidden : merge ???
            rst = self.code_block_directive(self.lexer)
            rst += self.indent_lines(self._lines)
            for output in self.outputs:
                if output.is_error:
                    rst += self.code_block_directive(self.error_lexer)
                    rst += self.indent_output(output)
            return rst + '\n'
        else:
            return '' # Fixme: ???

    ##############################################

    def to_code(self):

        source = ''
        for line in self._lines:
            # Fixme:
            if not line.startswith('pylab.show') and not line.startswith('plt.show'):
                source += line + '\n'
        return source

####################################################################################################

class GuardedCodeChunk(CodeChunk):

    MARKUP = 'e'
    ENCLOSING_MARKUP = True

####################################################################################################

class InteractiveCodeChunk(CodeChunk):

    MARKUP = 'i'
    ENCLOSING_MARKUP = True

    ##############################################

    def to_line_chunk(self):

        chunks = []
        for line in self._lines:
            if not line.strip():
                continue
            chunk = InteractiveLineCodeChunk(self._document, line)
            chunks.append(chunk)
        return chunks

####################################################################################################

class InteractiveLineCodeChunk(CodeChunk):

    ##############################################

    def __init__(self, document, line):

        super().__init__(document)
        self.append(line)

    ##############################################

    def to_rst(self):

        rst = super().to_rst()

        rst += self.code_block_directive('none')
        for output in self.outputs:
            if output.is_result:
                rst += self.indent_output(output)

        return rst + '\n'

####################################################################################################

class HiddenCodeChunk(CodeChunk):

    """ This class represents a hidden code block. """

    MARKUP = 'h'

    ##############################################

    def to_rst(self):

        return ''

####################################################################################################

class OutputChunk(Chunk):

    """ This class represents an output block. """

    MARKUP = 'o'

    ##############################################

    @property
    def code_chunk(self):
        return self._code_chunk

    @code_chunk.setter
    def code_chunk(self, value):
        self._code_chunk = value

    ##############################################

    def to_rst(self):

        rst = self.code_block_directive('none')
        for output in self._code_chunk.outputs:
            if output.is_stream:
                rst += self.indent_output(output)

        return rst + '\n'
