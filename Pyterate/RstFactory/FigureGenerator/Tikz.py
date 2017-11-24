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

import logging
import os
import shutil
import subprocess
import tempfile

from ..Dom import ImageChunk
from .Registry import ExtensionMetaclass
from Pyterate.Tools.Timestamp import timestamp

####################################################################################################

_module_logger = logging.getLogger(__name__)

####################################################################################################

LATEX_COMMAND = 'pdflatex'
# LATEX_COMMAND = 'lualatex'

####################################################################################################

class TikzImage:

    """ This class represents a Tikz figure. """

    _logger = _module_logger.getChild('TikzImage')

    ##############################################

    def __init__(self, tex_filename, source_directory, rst_directory):

        svg_filename = tex_filename.replace('.tex', '.svg')
        self._tex_path = os.path.join(source_directory, 'tex', tex_filename)
        self._rst_directory = rst_directory
        self._figure_path = svg_filename
        self._figure_real_path = os.path.join(rst_directory, svg_filename)

    ##############################################

    def __bool__(self):

        if os.path.exists(self._figure_real_path):
            return timestamp(self._tex_path) > timestamp(self._figure_real_path)
        else:
            return True

    ##############################################

    def make_figure(self):

        self._logger.info("\nMake Tikz figure " + self._tex_path)
        try:
            self._make_figure()
        except subprocess.CalledProcessError:
            self._logger.error("Failed to make Tikz figure", self._tex_path)

    ##############################################

    def _make_figure(self):

        dst_path = self._rst_directory

        with tempfile.TemporaryDirectory() as tmp_dir:
            # self._logger.info('Temporary directory ' + tmp_dir)

            # current_dir = os.curdir
            os.chdir(tmp_dir)
            shutil.copy(self._tex_path, '.')

            # Run LaTeX to generate PDF
            command = (
                LATEX_COMMAND,
                '-shell-escape',
                '-interaction=batchmode',
                # '-output-directory=' + tmp_dir,
                os.path.basename(self._tex_path),
            )
            dev_null = open(os.devnull, 'w')
            subprocess.check_call(command, stdout=dev_null, stderr=subprocess.STDOUT)

            basename = os.path.splitext(os.path.basename(self._tex_path))[0]
            svg_basename = basename + '.svg'
            svg_path = os.path.join(dst_path, svg_basename)
            shutil.copy(svg_basename, svg_path)

####################################################################################################

class TikzImageChunk(TikzImage, ImageChunk, metaclass=ExtensionMetaclass):

    """ This class represents an image block for a Tikz figure. """

    __markup__ = 'tz'

    ##############################################

    def __init__(self, line, source_directory, rst_directory):

        tex_filename, kwargs = ImageChunk.parse_args(line, self.__markup__)
        ImageChunk.__init__(self, None, **kwargs) # Fixme: _figure_path
        TikzImage.__init__(self, tex_filename, source_directory, rst_directory)
