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
import logging
import os

from nbformat import v4 as nbv4

from Pyterate.Tools.Timestamp import timestamp
from .Dom import Chunk

####################################################################################################

_module_logger = logging.getLogger(__name__)

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

        self._figure = figure

        super().__init__(document, figure_filename, **kwargs)

    ##############################################

    def to_code(self):

        return 'save_figure({}, "{}")'.format(self._figure, self.absolut_path)
