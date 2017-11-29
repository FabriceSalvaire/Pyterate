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
    'CodeChunk',
    'FigureChunk',
    'HiddenCodeChunk',
    'ImageChunk',
    'InteractiveChunk',
    'LiteralChunk',
    'LiteralIncludeChunk',
    'LocaleFigureChunk',
    'OutputChunk',
    'PythonIncludeChunk', # Fixme: !!!
    'RstChunk',
    'RstFormatChunk',
]

####################################################################################################

import ast
import astunparse
import base64
import logging
import os

from nbformat import v4 as nbv4

####################################################################################################

_module_logger = logging.getLogger(__name__)

####################################################################################################

try:
    from pypandoc import convert_text
except:
    _module_logger.warning('pypandoc is not installed')
    def convert_text(*args, **kwargs):
        return 'ERROR: pypandoc is not installed'

####################################################################################################

# Fixme: -> Node ???

class Chunk:

    """ This class represents a chunk of lines in the source. """

    MARKUP = None

    ##############################################

    def remove_markup(self, line, lstrip=False, strip=False):

        markup = self.language.enclose_markup(self.MARKUP)
        line = line[len(markup):]
        # Fixme: assume '#xxx# ...'
        if line.startswith(' '):
            line = line[1:]
        if strip:
            return line.strip()
        elif lstrip:
            return line.lstrip()
        else:
            return line

    ##############################################

    def parse_function_call(self, line):

        # "Module(body=[
        #     Expr(value=Call(
        #         func=Name(id='save_figure', ctx=Load()),
        #         args=[
        #             Name(id='figure', ctx=Load()),
        #             Str(s='my-figure.png')
        #         ],
        #         keywords=[
        #            keyword(arg='foo', value=Str(s='bar'))
        #         ]))])

        line = self.remove_markup(line, strip=True)

        module_ = ast.parse(line)
        expression = module_.body[0]
        call = expression.value
        if isinstance(call, ast.Call):
            return call
        else:
            raise NameError("Invalid call '{}'".format(line))

    ##############################################

    @staticmethod
    def to_ast(obj):

        if isinstance(obj, str):
            return ast.Str(obj)
        elif isinstance(obj, (int, float)):
            return ast.Num(obj)
        else:
            raise NotImplementedError

    ##############################################

    @classmethod
    def update_function_call(cls, call, *args, **kwargs):

        for obj in args:
            call.args.append(cls.to_ast(obj))
        for name, obj in kwargs.items():
            keyword = ast.keyword(name, cls.to_ast(obj))
            call.args.append(keyword)
        return astunparse.unparse(call).rstrip()

    ##############################################

    @staticmethod
    def symlink_source(source, target):

        if not os.path.exists(target):
            os.symlink(source, target)

    ##############################################

    @staticmethod
    def indent_lines(lines, indentation=4):

        indentation = ' '*indentation
        return '\n'.join([indentation + line.rstrip() for line in lines])

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

    def __bool__(self):
        return bool(self._lines)

    ##############################################

    # def __iter__(self):
    #     return iter(self._lines)

    ##############################################

    def append(self, line):

        self._lines.append(line)

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

        return convert_text(self.to_rst(), 'md', format='rst')

####################################################################################################

class ExecutedChunk(Chunk):

    ##############################################

    def __init__(self, document):

        super().__init__(document)

        self.outputs = []

    ##############################################

    def __bool__(self):

        for line in self._lines:
            if line.strip():
                return True
        return False

####################################################################################################

class ImageChunk(Chunk):

    ##############################################

    @staticmethod
    def parse_args(line, markup):

        # usage:
        # #tz# diode.tex width=500

        start = len(markup) + 2
        line = line[start:].strip()

        parts = [x for x in line.split(' ') if x]
        figure_path = parts[0]
        kwargs = {}
        for part in parts[1:]:
            if '=' in part:
                key, value = [x.strip() for x in part.split('=')]
                if key and value:
                    kwargs[key] = value
        return figure_path, kwargs

    ##############################################

    def __init__(self, document, figure_path, scale='', width='', height='', align=''):

        # Fixme: __init__, kwargs

        self._document = document
        self._figure_path = figure_path
        self._scale = scale
        self._width = width
        self._height = height
        self._align = align

    ##############################################

    def to_rst(self):

        args = (self._figure_path,)
        kwargs = dict(align='center')
        for key in ('scale', 'width', 'height'):
            value = getattr(self, '_' + key)
            if value:
                kwargs[key] = value
        return self.directive('image', args=args, kwargs=kwargs)

    ##############################################

    def to_base64(self):

        # Fixme:
        path = self.document.topic.join_rst_path(self._figure_path)
        with open(path, 'rb') as fh:
            image_base64 = base64.encodebytes(fh.read()).decode('ascii')
        return image_base64

    ##############################################

    def to_node(self):

        # Fixme:
        path = self.document.topic.join_rst_path(self._figure_path)
        if path.endswith('.png') and os.path.exists(path):
            return nbv4.new_output('display_data', data={'image/png': self.to_base64()})
        else:
            return None

####################################################################################################
####################################################################################################

class RstChunk(Chunk):

    """ This class represents a RST content. """

    MARKUP = '!'

    ##############################################

    def to_rst(self):
        return ''.join(self._lines) + '\n'

    ##############################################

    def append(self, line):

        # Fixme: common code
        super().append(self.remove_markup(line))

    ##############################################

    def has_format(self):

        for line in self._lines:
            if self.opening_format_markup in line:
                return True
        return False

    ##############################################

    def to_rst_format_chunk(self):

        return RstFormatChunk(self)

####################################################################################################

class RstFormatChunk(ExecutedChunk):

    ##############################################

    def __init__(self, rst_chunk):

        super().__init__(rst_chunk.document)

        self._lines = rst_chunk._lines

        self.guarded = False # Fixme: required, not ExecutedChunk

    ##############################################

    def to_rst(self):

        # Fixmes: more than one output

        return str(self.outputs[0]) + '\n'

    ##############################################

    def to_code(self):

        rst = ''.join(self._lines)
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

    MARKUP = None

    ##############################################

    def __init__(self, document):

        super().__init__(document)

        self.guarded = False

    ##############################################

    # @property
    # def is_guarded(self):
    #     return self._guarded

    # @guarded.setter
    # def is_guarded(self, value):
    #     self._guarded = value

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
                source += line
        return source

    ##############################################

    def to_interactive(self):

        chunks = []
        for line in self._lines:
            if not line.strip():
                continue
            chunk = InteractiveChunk(self._document, line)
            chunks.append(chunk)
        return chunks

####################################################################################################

class InteractiveChunk(CodeChunk):

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

    def append(self, line):

        super().append(self.remove_markup(line))

####################################################################################################

class OutputChunk(Chunk):

    """ This class represents an output block. """

    MARKUP = 'o'

    ##############################################

    def __init__(self, code_chunk):

        super().__init__(code_chunk.document)
        self._code_chunck = code_chunk

    ##############################################

    def to_rst(self):

        rst = self.code_block_directive('none')
        for output in self._code_chunck.outputs:
            if output.is_stream:
                rst += self.indent_output(output)

        return rst + '\n'

####################################################################################################

class LiteralChunk(Chunk):

    """ This class represents a literal block. """

    MARKUP = 'l'

    ##############################################

    def append(self, line):

        super().append(self.remove_markup(line))

    ##############################################

    def to_rst(self):

        if bool(self):
            source = self.indent_lines(self._lines)
            # rst = self.directive('class', args=('literal-chunk',)) # Don't work !
            return self.code_block_directive('py') + source + '\n'
        else:
            return ''

####################################################################################################

class LiteralIncludeChunk(Chunk):

    """ This class represents a literal include block. """

    MARKUP = 'itxt'

    ##############################################

    def __init__(self, document, line):

        self._document = document # Fixme:

        # Fixme: duplicated code with figure etc. ???
        include_path = self.remove_markup(line, strip=True)

        self._include_filename = os.path.basename(include_path)

        # Fixme: document ???
        source = document.topic.join_path(include_path)
        target = document.topic.join_rst_path(self._include_filename)
        self.symlink_source(source, target)

    ##############################################

    def to_rst(self):

        return self.directive('literalinclude', args=(self._include_filename,))

####################################################################################################

class PythonIncludeChunk(Chunk):

    """ This class represents a Python literal include block. """

    MARKUP = 'i'

    ##############################################

    def __init__(self, document, line):

        self._document = document # Fixme:

        self._include_path = self.remove_markup(line, strip=True)

        # Fixme: document ???
        # Fixme: relpath right ?
        source = os.path.relpath(document.topic.join_path(self._include_path), document.topic.rst_path)
        target = document.topic.join_rst_path(self._include_path)
        self.symlink_source(source, target)

    ##############################################

    def to_rst(self):

        return self.directive('getthecode', args=(self._include_path,), kwargs=dict(language=self.lexer))

####################################################################################################

class FigureChunk(ImageChunk):

    """ This class represents an image block for a saved figure. """

    MARKUP = 'fig'

    ##############################################

    def __init__(self, document, line):

        # Fixme: better way ???
        Chunk.__init__(self, document) # Fixme: document !!!
        self.append(line)

        self._rst_path = document.topic.rst_path

        self._call = self.parse_function_call(line)
        figure_filename = self._call.args[1].s # require a str

        super().__init__(document, figure_filename)

        self.guarded = False # Fixme: required, not ExecutedChunk

    ##############################################

    def to_code(self):

        return self.update_function_call(self._call, self._rst_path)

####################################################################################################

class LocaleFigureChunk(ImageChunk):

    """ This class represents an image block for a figure. """

    MARKUP = 'lfig'

    ##############################################

    def __init__(self, document, line):

        figure_path, kwargs = ImageChunk.parse_args(line, 'lfig') # Fixme: MARKUP
        figure_filename = os.path.basename(figure_path) # Fixme: ???
        figure_absolut_path = os.path.join(document.topic_path, figure_filename)
        link_path = os.path.join(document.topic_rst_path, figure_filename)
        super().__init__(document, figure_filename, **kwargs)

        self.symlink_source(figure_absolut_path, link_path)

####################################################################################################

class Dom:

    _logger = _module_logger.getChild('Dom')

    ##############################################

    def __init__(self):

        self._chunks = []

    ##############################################

    def __len__(self):
        return len(self._chunks)

    ##############################################

    def __iter__(self):
        return iter(self._chunks)

    ##############################################

    def append(self, chunk):

        # self._logger.debug(repr(chunk))
        self._chunks.append(chunk)

    ##############################################

    def iter_on_code_chunks(self):

        for chunck in self._chunks:
            if chunck.is_executed:
                yield chunck

    ##############################################

    @property
    def last_chunk(self):
        return self._chunks[-1]
