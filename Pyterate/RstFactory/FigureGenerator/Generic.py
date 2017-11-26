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
import subprocess

from ..Dom import ImageChunk
from .Registry import ExtensionMetaclass

####################################################################################################

_module_logger = logging.getLogger(__name__)

####################################################################################################

class GeneratedImage:

    """ This class represents a Tikz figure. """

    _logger = _module_logger.getChild('TikzImage')

    ##############################################

    def __init__(self, command, document, figure_name):

        self._command = command
        self._figure_name = figure_name

        self._rst_directory = document.topic_rst_path
        self._figure_real_path = os.path.join(self._rst_directory, self._figure_name)

    ##############################################

    def __bool__(self):

        # return False # it is up to the generator to decide if it overwrite
        if os.path.exists(self._figure_real_path):
            return self._query()
        else:
            return False

    ##############################################

    def make_figure(self):

        self._logger.info("\nMake figure " + self._figure_name)
        try:
            self._generate()
        except subprocess.CalledProcessError:
            self._logger.error("Failed to make figure", self._figure_name)

    ##############################################

    def _query(self):

        command = (
            self._command,
            '--query',
            self._figure_name,
            self._figure_real_path,
        )
        dev_null = open(os.devnull, 'w')
        rc = subprocess.check_output(command, stdout=dev_null, stderr=subprocess.STDOUT)
        return rc.strip() == 'uptodate'

    ##############################################

    def _generate(self):

        command = (
            self._command,
            self._figure_name,
            self._figure_real_path,
        )
        dev_null = open(os.devnull, 'w')
        subprocess.check_call(command, stdout=dev_null, stderr=subprocess.STDOUT)

####################################################################################################

class GeneratorImageChunk(GeneratedImage, ImageChunk, metaclass=ExtensionMetaclass):

    """ This class represents an image block for a generic generator. """

    __markup__ = 'gf'

    ##############################################

    def __init__(self, document, line):

        # ./bin/make-figure --kwargs="instrument='Guitare',tuning='Standard'" Musica.Figure.Fretboard.Fretboard figures/guitare-fretboard.tex

        command, figure_name, kwargs = ImageChunk.parse_args(line, self.__markup__)
        ImageChunk.__init__(self, None, **kwargs) # Fixme: _figure_path
        GeneratedImage.__init__(self, command, document, figure_name)
