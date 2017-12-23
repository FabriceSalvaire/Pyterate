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

from ..FigureMarkups import ExternalFigureChunk

####################################################################################################

_module_logger = logging.getLogger(__name__)

####################################################################################################

LATEX_COMMAND = 'pdflatex'
# LATEX_COMMAND = 'lualatex'

####################################################################################################

class TikzChunk(ExternalFigureChunk):

    """ This class represents an image block for a Tikz figure. """

    COMMAND = 'tikz'

    _logger = _module_logger.getChild('TikzImage')

    ##############################################

    def __init__(self, document, tex_filename, **kwargs):

        figure_path = tex_filename.replace('.tex', '.svg')
        source_path = document.topic.join_path('tex', tex_filename) # Fixme: tex directory ???

        super().__init__(document, source_path, figure_path, **kwargs)

    ##############################################

    def make_figure(self):

        self._logger.info("\nMake Tikz figure " + self.source_path)
        try:
            self._make_figure()
        except subprocess.CalledProcessError:
            self._logger.error("Failed to make Tikz figure", self.source_path)

    ##############################################

    def _make_figure(self):

        with tempfile.TemporaryDirectory() as tmp_dir:
            # self._logger.info('Temporary directory ' + tmp_dir)

            # current_dir = os.curdir
            os.chdir(tmp_dir)
            shutil.copy(self.source_path, '.') # Fixme: symlink

            # Run LaTeX to generate PDF
            command = (
                LATEX_COMMAND,
                '-shell-escape',
                '-interaction=batchmode',
                # '-output-directory=' + tmp_dir,
                os.path.basename(self.source_path),
            )
            dev_null = open(os.devnull, 'w')
            subprocess.check_call(command, stdout=dev_null, stderr=subprocess.STDOUT)

            shutil.copy(self.path, self.absolut_path)
