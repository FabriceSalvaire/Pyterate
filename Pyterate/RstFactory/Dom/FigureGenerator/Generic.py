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

from ..FigureMarkups import ExternalFigureChunk

####################################################################################################

_module_logger = logging.getLogger(__name__)

####################################################################################################

class GeneratedImageChunk:

    """ This class represents a Tikz figure. """

    COMMAND = 'generated_figure'

    _logger = _module_logger.getChild('TikzImage')

    ##############################################

    def __init__(self, document, command, figure_path, **kwargs):

        super().__init__(document, figure_path, **kwargs)

        self._command = command

    ##############################################

    def __bool__(self):

        # return False # it is up to the generator to decide if it overwrite
        if os.path.exists(self.absolut_path):
            return self._query()
        else:
            return False

    ##############################################

    def make_figure(self):

        self._logger.info("\nMake figure " + self.path)
        try:
            self._generate()
        except subprocess.CalledProcessError:
            self._logger.error("Failed to make figure", self.path)

    ##############################################

    def _query(self):

        command = (
            self._command,
            '--query',
            self.path,
            self.absolut_path,
        )
        dev_null = open(os.devnull, 'w')
        rc = subprocess.check_output(command, stdout=dev_null, stderr=subprocess.STDOUT)
        return rc.strip() == 'uptodate'

    ##############################################

    def _generate(self):

        command = (
            self._command,
            self.path,
            self.absolut_path,
        )
        dev_null = open(os.devnull, 'w')
        subprocess.check_call(command, stdout=dev_null, stderr=subprocess.STDOUT)
