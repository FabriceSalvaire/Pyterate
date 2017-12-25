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
    'ExternalFigureChunk',
    'LocaleFigureChunk',
    'SaveFigureChunk',
]

####################################################################################################

import base64
import json
import logging
import os

from nbformat import v4 as nbv4

from Pyterate.Tools.Timestamp import timestamp
from .Dom import Chunk

####################################################################################################

# _module_logger = logging.getLogger(__name__)

####################################################################################################

class ImageChunk(Chunk):

    COMMAND = None

    ##############################################

    def __init__(self, document, path, **kwargs):

        self._document = document
        self._path = path
        self._absolut_path = self.document.topic.join_rst_path(path)

        self._scale = kwargs.get('scale', None)
        self._width = kwargs.get('width', None)
        self._height = kwargs.get('height', None)
        self._align = kwargs.get('align', None)

    ##############################################

    @property
    def path(self):
        return self._path

    @property
    def absolut_path(self):
        return self._absolut_path

    ##############################################

    def to_rst(self):

        args = (self._path,)
        kwargs = dict(align='center')
        for key in ('scale', 'width', 'height'):
            value = getattr(self, '_' + key)
            if value:
                kwargs[key] = value
        return self.directive('image', args=args, kwargs=kwargs)

    ##############################################

    def to_base64(self):

        with open(self._absolut_path, 'rb') as fh:
            image_base64 = base64.encodebytes(fh.read()).decode('ascii')

        return image_base64

    ##############################################

    def to_node(self):

        # Using attachments
        #
        # {
        #  "attachments": {
        #   "foo.png": {
        #    "image/png": "iVBO...mCC"
        #   },
        #   "foo.svg": {
        #    "image/svg+xml": [
        #     "PD9...nPgo="
        #    ]
        #   }
        #  },
        #  "cell_type": "markdown",
        #  "metadata": {},
        #  "source": [
        #   "![foo.png](attachment:foo.png)\n",
        #   "\n",
        #   "![foo.svg](attachment:foo.svg)"
        #  ]
        # },

        # Directly in Markdown
        #
        # ![svg image](data:image/svg+xml,URL_ENCODED_SVG]

        if self.path.endswith('.png') and os.path.exists(self.absolut_path):
            return nbv4.new_output('display_data', data={'image/png': self.to_base64()})
        else:
            return None

####################################################################################################

class ExternalFigureChunk(ImageChunk):

    ##############################################

    def __init__(self, document, source_path, figure_path, **kwargs):

        super().__init__(document, figure_path, **kwargs)

        self._source_path = source_path # Fixme: absolut ???

    ##############################################

    @property
    def source_path(self):
        return self._source_path

    ##############################################

    def __bool__(self):

        if os.path.exists(self.absolut_path):
            return timestamp(self._source_path) > timestamp(self.absolut_path)
        else:
            return True

####################################################################################################

class LocaleFigureChunk(ImageChunk):

    """ This class represents an image block for a figure. """

    COMMAND = 'image'

    ##############################################

    def __init__(self, document, source, **kwargs):

        target = document.symlink_source(source)

        super().__init__(document, target, **kwargs)

####################################################################################################

class SaveFigureChunk(ImageChunk):

    """ This class represents an image block for a saved figure. """

    COMMAND = 'save_figure'

    ##############################################

    def __init__(self, document, figure, figure_filename, **kwargs):

        super().__init__(document, figure_filename, **kwargs)

        self._figure = figure

        # Fixme: don't call CodeChunk ctor / Mixin ?

    ##############################################

    def to_code(self):

        return 'save_figure({}, "{}")'.format(self._figure, self.absolut_path)

####################################################################################################

class TableFigureChunk(Chunk):

    """ This class represents a table figure. """

    COMMAND = 'table'

    ##############################################

    def __init__(self, document, name, columns=None, str_format='{}'):

        super().__init__(document)

        self._name = name
        self._columns = columns
        self._format = str_format

        self._column_length = []

    ##############################################

    def _iter_on_columns(self):

        return enumerate(self._columns)

    ##############################################

    def _update_column_length(self, i, value):

        self._column_length[i] = max(len(str(value)), self._column_length[i])

    ##############################################

    def _rule(self, rule_chr):

        column_rule = [rule_chr*self._column_length[i]
                       for i in range(len(self._column_length))]

        return ' '.join(column_rule) + '\n'

    ##############################################

    def _format_line(self, values):

        padded_values = [' '*(self._column_length[i] - len(value)) + value
                         for i, value in enumerate(values)]

        return ' '.join(padded_values) + '\n'

    ##############################################

    def to_code(self):

        return 'export_value({})'.format(self._name)

    ##############################################

    def to_rst(self):

        json_data = self.outputs[0].result # Fixme: str()
        table = json.loads(json_data[1:-1])

        number_of_columns = len(table[0])
        str_table = []
        self._column_length = [0]*number_of_columns
        for line in table:
            if len(line) != number_of_columns:
                raise NameError('Invalid table')
            str_line = []
            for i, value in enumerate(line):
                str_value = self._format.format(value)
                self._update_column_length(i, str_value)
                str_line.append(str_value)
            str_table.append(str_line)

        rst = ''

        if self._columns:
            for i, column in self._iter_on_columns():
                self._update_column_length(i, column)
            rst += self._rule('=')
            rst += self._format_line(self._columns)
            rst += self._rule('=')

        for line in str_table:
            rst += self._format_line(line)

        if self._columns:
            rst += self._rule('=')

        return rst + '\n'
