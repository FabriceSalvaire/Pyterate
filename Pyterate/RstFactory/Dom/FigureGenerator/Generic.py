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

from ..FigureNodes import ExternalFigureNode

####################################################################################################

_module_logger = logging.getLogger(__name__)

####################################################################################################

class GeneratedImageNode(ExternalFigureNode):

    """This class represents a generated figure.

    Syntax::

        generated_figure(command, figure_filename, arg1=value1, ...)

    Command API::

        # Test if the figure must be regenerated
        # return "uptodate" or nothing
        command --query absolut_figure_path

        command --arg1=value1 ... absolut_figure_path

    """

    COMMAND = 'generated_figure'

    _logger = _module_logger.getChild('GeneratedImageNode')

    ##############################################

    def __init__(self, document, command, figure_path, **kwargs):
        source_path = ''  # Fixme: passed to Path()
        super().__init__(document, source_path, figure_path, **kwargs)
        self._command = command
        self._kwargs = {
            key: value
            for key, value in kwargs.items()
            if key not in ('align', 'scale', 'height', 'width')
        }

    ##############################################

    def __bool__(self):
        # it is up to the generator to decide if it overwrite
        if self.absolut_path.exists():
            return self._query()
        else:
            return True

    ##############################################

    def make_figure(self):
        self._logger.info(os.linesep + 'Make figure {}'.format(self.absolut_path))
        try:
            self._generate()
        except subprocess.CalledProcessError:
            self._logger.error('Failed to make figure', self.absolut_path)

    ##############################################

    def _query(self):
        self._logger.info(os.linesep + 'Query figure {}'.format(self.absolut_path))
        command = (
            self._command,
            '--query',
            self.absolut_path,
        )
        rc = subprocess.check_output(command, stderr=subprocess.STDOUT)
        return rc.strip() != 'uptodate'

    ##############################################

    def _generate(self):
        command = (
            self._command,
            self.absolut_path,
        )
        # Fixme: command not found
        subprocess.check_call(command, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
