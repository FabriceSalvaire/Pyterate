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

# Fixme: default lexer python3

# Fixme: These classes do several tasks
#  decode input
#  store data
#  __str__ generate RST
#  to_python

####################################################################################################

__all__ = [
    'Dom',
    'Chunk', # Fixme: -> Node ???
    'RstChunk',
    'CodeChunk',
    'HiddenCodeChunk',
    'LitteralIncludeChunk',
    'PythonIncludeChunk',
    'ImageChunk',
    'FigureChunk',
    'LocaleFigureChunk',
    'OutputChunk',
    'RstFormatChunk',
]

####################################################################################################

import ast
import astunparse
import os

####################################################################################################

# Must fit Python, RST and LaTeX formulae
OPENING_FORMAT_MARKUP = '@<@'
CLOSING_FORMAT_MARKUP = '@>@'
ESCAPED_OPENING_FORMAT_MARKUP = '@@<<@@'
ESCAPED_CLOSING_FORMAT_MARKUP = '@@>>@@'

####################################################################################################

class Chunk:

    """ This class represents a chunk of lines in the source. """

    MARKUP = None

    ##############################################

    @classmethod
    def remove_markup(cls, line, lstrip=True, strip=False):

        line = line[len(cls.MARKUP):]
        if strip:
            return line.strip()
        elif lstrip:
            return line.lstrip()
        else:
            return line

    ##############################################

    @classmethod
    def parse_function_call(cls, line):

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

        line = cls.remove_markup(line, strip=True)

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

    def __init__(self):

        self._lines = []

    ##############################################

    def __bool__(self):
        return bool(self._lines)

    ##############################################

    def append(self, line):

        self._lines.append(line)

    ##############################################

    @property
    def is_executed(self):
        return hasattr(self, 'to_python')

####################################################################################################

class ExecutedChunk(Chunk):

    ##############################################

    def __init__(self):

        super().__init__()

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

    def __init__(self, figure_path, scale='', width='', height='', align=''):

        # Fixme: kwargs

        self._figure_path = figure_path
        self._scale = scale
        self._width = width
        self._height = height
        self._align = align

    ##############################################

    def __str__(self):

        # Fixme: jinja

        template = '''
.. image:: {0._figure_path}
  :align: center
'''
        rst_code = template.format(self)
        for key in ('scale', 'width', 'height'):
            value = getattr(self, '_' + key)
            if value:
                rst_code += '  :{0}: {1}\n'.format(key, value)
        return rst_code + '\n'

####################################################################################################
####################################################################################################

class RstChunk(Chunk):

    """ This class represents a RST content. """

    MARKUP = '#!#'

    ##############################################

    def __str__(self):
        return ''.join(self._lines)

    ##############################################

    def has_format(self):

        for line in self._lines:
            if OPENING_FORMAT_MARKUP in line:
                return True
        return False

    ##############################################

    def to_rst_format_chunk(self):

        return RstFormatChunk(self)

####################################################################################################

class RstFormatChunk(ExecutedChunk):

    ##############################################

    def __init__(self, rst_chunk):

        super().__init__()

        self._lines = rst_chunk._lines

    ##############################################

    def __str__(self):

        # Fixmes: more than one output

        return str(self.outputs[0])

    ##############################################

    def to_python(self):

        rst = ''.join(self._lines)
        rst = rst.replace('{', '{{') # to escape them
        rst = rst.replace('}', '}}')
        rst = rst.replace(OPENING_FORMAT_MARKUP, '{')
        rst = rst.replace(CLOSING_FORMAT_MARKUP, '}')
        rst = rst.replace(ESCAPED_OPENING_FORMAT_MARKUP, OPENING_FORMAT_MARKUP)
        rst = rst.replace(ESCAPED_CLOSING_FORMAT_MARKUP, CLOSING_FORMAT_MARKUP)

        return 'print(r"""' + rst + '""".format(**locals()))\n'

####################################################################################################

class CodeChunk(ExecutedChunk):

    """ This class represents a code block. """

    MARKUP = None

    ##############################################

    def __str__(self):

        # Fixme: jinja

        if bool(self):
            source = ''.join(['    ' + line for line in self._lines])
            return '\n.. code-block:: py3\n\n' + source + '\n'
        else:
            return ''

    ##############################################

    def to_python(self):

        source = ''
        for line in self._lines:
            # Fixme:
            if not line.startswith('pylab.show') and not line.startswith('plt.show'):
                source += line
        return source

####################################################################################################

class HiddenCodeChunk(CodeChunk):

    """ This class represents a hidden code block. """

    MARKUP = '#h#'

    ##############################################

    def append(self, line):

        super().append(self.remove_markup(line))

    ##############################################

    def __str__(self):

        return ''

####################################################################################################

class OutputChunk(Chunk):

    """ This class represents an output block. """

    MARKUP = '#o#'

    ##############################################

    def __init__(self, code_chunk):

        super().__init__()
        self._code_chunck = code_chunk

    ##############################################

    def __str__(self):

        # PythonConsoleLexer    pycon
        # Python3TracebackLexer py3tb

        rst = '''
.. code-block:: none

'''
        for output in self._code_chunck.outputs:
            for line in str(output):
                rst += ' '*4 + line
        rst += '\n'

        return rst

####################################################################################################

class LitteralIncludeChunk(Chunk):

    """ This class represents a litteral include block. """

    MARKUP = '#itxt#'

    ##############################################

    def __init__(self, document, line):

        # Fixme: duplicated code with figure etc. ???

        include_path = self.remove_markup(line, strip=True)

        self._include_filename = os.path.basename(include_path)

        # Fixme: document ???
        source = document.topic.join_path(include_path)
        target = document.topic.join_rst_path(self._include_filename)
        self.symlink_source(source, target)

    ##############################################

    def __str__(self):

        # Fixme: jinja

        template = '''
.. literalinclude:: {}

'''
        return template.format(self._include_filename)

####################################################################################################

class PythonIncludeChunk(Chunk):

    """ This class represents a Python litteral include block. """

    MARKUP = '#i#'

    ##############################################

    def __init__(self, document, line):

        self._include_path = self.remove_markup(line, strip=True)

        # Fixme: document ???
        # Fixme: relpath right ?
        source = os.path.relpath(document.topic.join_path(self._include_path), document.topic.rst_path)
        target = document.topic.join_rst_path(self._include_path)
        self.symlink_source(source, target)

    ##############################################

    def __str__(self):

        # Fixme: jinja

        template = '''
.. getthecode:: {}
  :language: python3

'''
        return template.format(self._include_path)

####################################################################################################

class FigureChunk(ImageChunk):

    """ This class represents an image block for a saved figure. """

    MARKUP = '#fig#'

    ##############################################

    def __init__(self, document, line):

        # Fixme: better way ???
        Chunk.__init__(self)
        self.append(line)

        self._rst_path = document.topic.rst_path

        self._call = self.parse_function_call(line)
        figure_filename = self._call.args[1].s # require a str

        super().__init__(figure_filename)

    ##############################################

    def to_python(self):

        return self.update_function_call(self._call, self._rst_path)

####################################################################################################

class LocaleFigureChunk(ImageChunk):

    """ This class represents an image block for a figure. """

    MARKUP = '#lfig#'

    ##############################################

    def __init__(self, document, line):

        figure_path, kwargs = ImageChunk.parse_args(line, 'lfig') # Fixme: MARKUP
        figure_filename = os.path.basename(figure_path)
        figure_absolut_path = os.path.join(document.topic_path, document.topic_rst_path)
        link_path = os.path.join(rst_directory, figure_filename)
        super().__init__(figure_filename, **kwargs)

        self.symlink_source(figure_absolut_path, link_path)

####################################################################################################

class Dom(list):

    # __iter__
    # append

    ##############################################

    def iter_on_code_chunks(self):

        for chunck in self:
            if chunck.is_executed:
                yield chunck

    ##############################################

    @property
    def last_chunk(self):
        return self[-1]
