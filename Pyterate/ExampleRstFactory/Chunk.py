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

# Fixme: python console lexer pycon
# Fixme: default lexer python3

####################################################################################################

__all__ = [
    'Chunk',
    'RstChunk',
    'CodeChunk',
    'HiddenCodeChunk',
    'LitteralIncludeChunk',
    'PythonIncludeChunk',
    'ImageChunk',
    'FigureChunk',
    'LocaleFigureChunk',
    'StdoutChunk',
    'OutputChunk',
    'RstFormatChunk',
    'Chunks',
]

####################################################################################################

import os

####################################################################################################

OPENING_FORMAT_MARKUP = '@<@'
CLOSING_FORMAT_MARKUP = '@>@'

####################################################################################################

class Chunk:

    """ This class represents a chunk of lines in the source. """

    ##############################################

    def __init__(self):

        self._lines = []

    ##############################################

    def append(self, line):

        self._lines.append(line)

####################################################################################################

class RstChunk(Chunk):

    """ This class represents a RST content. """

    ##############################################

    def __bool__(self):

        return bool(self._lines)

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

    def to_rst_format_chunk(self, example, stdout_chunk_index):

        return RstFormatChunk(example, self, stdout_chunk_index)

####################################################################################################

class CodeChunk(Chunk):

    """ This class represents a code block. """

    ##############################################

    def append_head(self, line):

        self._lines.insert(1, line)

    ##############################################

    def __bool__(self):

        for line in self._lines:
            if line.strip():
                return True
        return False

    ##############################################

    def __str__(self):

        if bool(self):
            source = ''.join(['    ' + line for line in self._lines])
            return '\n.. code-block:: py3\n\n' + source + '\n'
        else:
            return ''

    ##############################################

    def to_python(self):

        source = ''
        for line in self._lines:
            if not line.startswith('pylab.show') and not line.startswith('plt.show'):
                source += line
        return source

####################################################################################################

class HiddenCodeChunk(CodeChunk):

    """ This class represents a code block. """

    ##############################################

    def append(self, line):

        self._lines.append(line[len('#h# '):])

    ##############################################

    def __str__(self):

        return ''

####################################################################################################

class LitteralIncludeChunk(Chunk):

    """ This class represents a litteral include block. """

    ##############################################

    def __init__(self, example, line):

        # Fixme: duplicated code with figure etc. ???
        include_path = line.replace('#itxt# ', '').strip()
        self._include_filename = os.path.basename(include_path)
        source = example.topic.join_path(include_path)
        target = example.topic.join_rst_path(self._include_filename)
        if not os.path.exists(target):
            os.symlink(source, target)

    ##############################################

    def __str__(self):

        template = '''
.. literalinclude:: {}

'''
        return template.format(self._include_filename)

####################################################################################################

class PythonIncludeChunk(Chunk):

    """ This class represents a Python litteral include block. """

    ##############################################

    def __init__(self, example, line):

        self._include_path = line.replace('#i# ', '').strip()
        # Fixme: relpath right ?
        source = os.path.relpath(example.topic.join_path(self._include_path), example.topic.rst_path)
        target = example.topic.join_rst_path(self._include_path)
        if not os.path.exists(target):
            os.symlink(source, target)

    ##############################################

    def __str__(self):

        template = '''
.. getthecode:: {}
  :language: python3

'''
        return template.format(self._include_path)

####################################################################################################

class ImageChunk(Chunk):

    ##############################################

    @staticmethod
    def parse_args(line, markup):

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

        self._figure_path = figure_path
        self._scale = scale
        self._width = width
        self._height = height
        self._align = align

    ##############################################

    def __str__(self):

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

class FigureChunk(ImageChunk):

    """ This class represents an image block for a saved figure. """

    ##############################################

    def __init__(self, line):

        # weak ...
        Chunk.__init__(self) # Fixme: better way ???
        self.append(line)
        figure_path = line[line.rindex(", '")+3:line.rindex("')")]
        super().__init__(figure_path)

    ##############################################

    def to_python(self):

        return self._lines[0][len('#fig# '):]

####################################################################################################

class LocaleFigureChunk(ImageChunk):

    """ This class represents an image block for a figure. """

    ##############################################

    def __init__(self, line, source_directory, rst_directory):

        figure_path, kwargs = ImageChunk.parse_args(line, 'lfig')
        figure_filename = os.path.basename(figure_path)
        figure_absolut_path = os.path.join(source_directory, figure_path)
        link_path = os.path.join(rst_directory, figure_filename)
        super().__init__(figure_filename, **kwargs)

        if not os.path.exists(link_path):
            os.symlink(figure_absolut_path, link_path)

####################################################################################################

class StdoutChunk(Chunk):

    """ This class represents an output block. """

    ##############################################

    def __init__(self, example, stdout_chunk_index):

        self._example = example
        self._stdout_chunk_index = stdout_chunk_index

    ##############################################

    @property
    def stdout_chunk_index(self):
        return self._stdout_chunk_index

####################################################################################################

class OutputChunk(StdoutChunk):

    ##############################################

    def __init__(self, example, line, stdout_chunk_index):

        StdoutChunk.__init__(self, example, stdout_chunk_index)
        self._line = line

    ##############################################

    def __str__(self):

        # Fixme: use content ???
        slice_, content = self._example.stdout_chunk(self._stdout_chunk_index)
        lower = slice_.start
        upper = slice_.stop -1
        # Sphynx count \f as newline
        if self._stdout_chunk_index:
            lower += self._stdout_chunk_index
            upper += self._stdout_chunk_index

        template = '''
.. literalinclude:: {}
    :lines: {}-{}

'''
        return template.format(os.path.basename(self._example.stdout_path), lower+1, upper+1)

    ##############################################

    def to_python(self):

        return 'print("\f #{}")\n'.format(self._stdout_chunk_index)

####################################################################################################

class RstFormatChunk(StdoutChunk):

    ##############################################

    def __init__(self, example, rst_chunk, stdout_chunk_index):

        StdoutChunk.__init__(self, example, stdout_chunk_index)
        self._lines = rst_chunk._lines

    ##############################################

    def __str__(self):

        slice_, content = self._example.stdout_chunk(self._stdout_chunk_index)
        return content

    ##############################################

    def to_python(self):

        rst = ''.join(self._lines)
        rst = rst.replace('{', '{{') # to escape them
        rst = rst.replace('}', '}}')
        rst = rst.replace(OPENING_FORMAT_MARKUP, '{')
        rst = rst.replace(CLOSING_FORMAT_MARKUP, '}')
        rst = rst.replace('@@<<@@', OPENING_FORMAT_MARKUP)
        rst = rst.replace('@@>>@@', CLOSING_FORMAT_MARKUP)
        marker = "\f #{}".format(self._stdout_chunk_index)
        return 'print(r"""' + rst + '""".format(**locals()))\n' + 'print("' + marker + '")\n'

####################################################################################################

class Chunks(list):
    pass
