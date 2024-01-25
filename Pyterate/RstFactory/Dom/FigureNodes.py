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

"""This module contains figure nodes.

"""

####################################################################################################

__all__ = [
    'ExternalFigureNode',
    'ImageNode',
    'LocaleFigureNode',
    'SaveFigureNode',
]

####################################################################################################

from pathlib import Path
import base64
import json
import logging
import os
import subprocess
from typing import TYPE_CHECKING, Iterable

from nbformat import v4 as nbv4

from Pyterate.Tools.Timestamp import timestamp
from .Dom import Node, MystMixin

if TYPE_CHECKING:
    from ..Document import Document

####################################################################################################

NEWLINE = os.linesep

_module_logger = logging.getLogger(__name__)

####################################################################################################

class ImageNode(MystMixin, Node):

    """Class to implement an image node.

    Accept these image reST arguments:

      * scale
      * with
      * height
      * align

    """

    COMMAND = None

    _logger = _module_logger.getChild('ImageNode')

    ##############################################

    @classmethod
    def __check_environment(cls):
        cls.check_command('convert', '--version', help='ImageMagick https://imagemagick.org')

    ##############################################

    def __init__(self, document: 'Document', path, **kwargs) -> None:
        self._document = document
        self._path = Path(path)
        self._absolut_path = self.document.topic.join_rst_path(path)
        self._scale = kwargs.get('scale', None)
        self._width = kwargs.get('width', None)
        self._height = kwargs.get('height', None)
        self._align = kwargs.get('align', None)

    ##############################################

    @property
    def path(self) -> Path:
        return self._path

    @property
    def absolut_path(self) -> Path:
        return self._absolut_path

    ##############################################

    def _to_rst(self, use_myst: bool = False) -> str:
        # https://myst-parser.readthedocs.io/en/latest/syntax/images_and_figures.html#block-level-images
        args = (self._path,)
        kwargs = dict(align='center')   # Fixme: align
        for key in ('scale', 'width', 'height'):
            value = getattr(self, '_' + key)
            if value:
                kwargs[key] = value
        rst = self.directive('image', args=args, kwargs=kwargs, use_myst=use_myst)
        rst += self.close_directive(use_myst)
        return rst

    ##############################################

    def to_base64(self, path=None) -> str:
        if path is None:
            path = self._absolut_path
        with open(path, 'rb') as fh:
            data = fh.read()
            image_base64 = base64.encodebytes(data)
            image_base64 = image_base64.decode('ascii')
            # image_base64 = image_base64.replace(NEWLINE, '')
        return image_base64

    ##############################################

    def to_output_cell(self):

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

        if not self.absolut_path.exists():
            mime_type = None
        elif self.path.suffix == '.png':
            mime_type = 'image/png'
        elif self.path.suffix == '.svg':
            mime_type = 'image/svg+xml'
        else:
            mime_type = None

        if mime_type is not None:
            return nbv4.new_output('display_data', data={mime_type: self.to_base64()})
        else:
            self._logger.warning('unsupported image format {}'.format(self.absolut_path))
            return None

    ##############################################

    def to_cell(self):
        path = None
        if not self.absolut_path.exists():
            mime_type = None
        elif self.path.suffix == '.png':
            mime_type = 'image/png'
        elif self.path.suffix == '.svg':
            # Fixme: Jupyter does not display SVG ???
            mime_type = 'image/png'
            path = self._absolut_path.parent.joinpath(self._absolut_path.stem + '.png')
            self._logger.warning('convert {} -> {}'.format(self._absolut_path, path))
            # Fixme: require convert ...
            command = ('convert', 'svg:' + self._absolut_path.name, 'png:' + path.name)
            subprocess.check_call(command, cwd=str(self._absolut_path.parent), shell=False)
        else:
            mime_type = None

        if mime_type is not None:
            markdown = "![{0}](attachment:{0})".format(self.path)
            attachments = {
                str(self.path): {
                    mime_type: self.to_base64(path),
                }
            }
            cell = nbv4.new_markdown_cell(markdown, attachments=attachments)
            return cell
        else:
            self._logger.warning('unsupported image format {}'.format(self.absolut_path))
            return None

####################################################################################################

class ExternalFigureNode(ImageNode):

    ##############################################

    def __init__(self, document: 'Document', source_path, figure_path, **kwargs):
        super().__init__(document, figure_path, **kwargs)
        self._source_path = Path(source_path)   # Fixme: absolut ???

    ##############################################

    @property
    def source_path(self) -> Path:
        return self._source_path

    ##############################################

    def __bool__(self) -> bool:
        if self.absolut_path.exists():
            return timestamp(self._source_path) > timestamp(self.absolut_path)
        else:
            return True

####################################################################################################

class LocaleFigureNode(ImageNode):

    """ This class represents an image block for a figure. """

    COMMAND = 'image'

    ##############################################

    def __init__(self, document: 'Document', source, **kwargs) -> None:
        target = document.symlink_source(Path(source))
        super().__init__(document, target, **kwargs)

####################################################################################################

class SaveFigureNode(ImageNode):

    """ This class represents an image block for a saved figure. """

    COMMAND = 'save_figure'

    ##############################################

    def __init__(self, document: 'Document', figure, figure_filename, **kwargs) -> None:
        super().__init__(document, figure_filename, **kwargs)
        self._figure = figure

        # Fixme: don't call CodeNode ctor / Mixin ?

    ##############################################

    def to_code(self) -> str:
        return 'save_figure({}, "{}")'.format(self._figure, self.absolut_path)

####################################################################################################

class TableFigureNode(MystMixin, Node):

    """ This class represents a table figure. """

    COMMAND = 'table'

    _PANDOC_MARKDOWN = 'markdown_strict'

    ##############################################

    def __init__(
        self,
        document: 'Document',
        table,
        columns=None,
        str_format='{}',
    ) -> None:
        super().__init__(document)
        self._table = table
        self._columns = columns
        self._format = str_format
        self._column_length = []

    ##############################################

    def _iter_on_columns(self) -> Iterable[[int, str]]:
        return enumerate(self._columns)

    ##############################################

    def _update_column_length(self, i: int, value) -> None:
        self._column_length[i] = max(len(str(value)), self._column_length[i])

    ##############################################

    def _format_line(self, values: list[str], use_myst: bool = False) -> str:
        padded_values = [' '*(self._column_length[i] - len(value)) + value
                         for i, value in enumerate(values)]
        sep = ' | ' if use_myst else ' '
        _ = sep.join(padded_values)
        if use_myst:
            _ = f'| {_} |'
        return _ + NEWLINE

    ##############################################

    def _rule(self, use_myst: bool = False) -> str:
        rule_chr = '-' if use_myst else '='
        column_rule = [rule_chr*self._column_length[i]
                       for i in range(len(self._column_length))]
        return self._format_line(column_rule, use_myst)

    ##############################################

    def _table_is_not_exported(self) -> bool:
        return isinstance(self._table, str)

    ##############################################

    def to_code(self) -> str:
        # Fixme: API -> to figure ???
        if self._table_is_not_exported():
            return f'export_value({self._table})'
        else:
            return None

    ##############################################

    def _exported_value(self) -> list:
        # Fixme: 0 str() ???
        json_data = self.outputs[0].result
        return json.loads(json_data[1:-1])

    ##############################################

    def _to_rst(self, use_myst: bool = False) -> str:
        # see https://github.com/ralsina/rst-cheatsheet/blob/master/rst-cheatsheet.rst
        if self._table_is_not_exported():
            table = self._exported_value()
        else:
            table = self._table
        # build a table of str
        str_table = []
        number_of_columns = len(table[0])
        self._column_length = [0]*number_of_columns
        for line in table:
            if len(line) != number_of_columns:
                raise NameError('Invalid table')
            str_line = []
            for i, value in enumerate(line):
                _ = self._format.format(value)
                self._update_column_length(i, _)
                str_line.append(_)
            str_table.append(str_line)

        rst = ''
        rule = self._rule(use_myst)
        if not use_myst:
            rst += rule
        if self._columns:
            for i, column in self._iter_on_columns():
                self._update_column_length(i, column)
            rst += self._format_line(self._columns, use_myst)
        if not self._columns and use_myst:
            rst += self._format_line(['...']*number_of_columns, use_myst)
        if self._columns or use_myst:
            rst += rule
        for line in str_table:
            rst += self._format_line(line, use_myst)
        if not use_myst:
            rst += rule
        return rst + NEWLINE

    ##############################################

    # def to_markdown(self) -> str:
    #     markdown = super().to_markdown()
    #     print(markdown)
    #     return 'Table:\n' + markdown
