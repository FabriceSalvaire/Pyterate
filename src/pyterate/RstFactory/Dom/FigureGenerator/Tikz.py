####################################################################################################
#
# Pyterate - Sphinx add-ons to create API documentation for Python projects
# Copyright (C) 2014 Fabrice Salvaire
# SPDX-License-Identifier: GPL-3.0-or-later
#
####################################################################################################

####################################################################################################

from pathlib import Path
import logging
import os
import shutil

import subprocess
import tempfile

from ..FigureNodes import ExternalFigureNode

####################################################################################################

_module_logger = logging.getLogger(__name__)

####################################################################################################

class TikzNode(ExternalFigureNode):

    """ This class represents an image block for a Tikz figure. """

    COMMAND = 'tikz'

    LATEX_COMMAND = 'pdflatex'
    # LATEX_COMMAND = 'lualatex'

    _logger = _module_logger.getChild('TikzNode')

    ##############################################

    @classmethod
    def check_environment(cls):
        cls.check_command(cls.LATEX_COMMAND, '--version', help='LaTeX')

    ##############################################

    def __init__(self, document, tex_filename, **kwargs):
        tex_filename = Path(tex_filename)
        figure_path = tex_filename.parent.joinpath(tex_filename.stem + '.svg')  # Fixme: monkey patch pathlib ?
        source_path = document.topic.join_path('tex', tex_filename)  # Fixme: tex directory ???
        super().__init__(document, source_path, figure_path, **kwargs)

    ##############################################

    def make_figure(self):
        self._logger.info(os.linesep + 'Make Tikz figure {}'.format(self.source_path))
        try:
            self._make_figure()
        except subprocess.CalledProcessError:
            self._logger.error("Failed to make Tikz figure", self.source_path)

    ##############################################

    def _make_figure(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            # self._logger.info('Temporary directory ' + tmp_dir)
            current_dir = os.getcwd()
            os.chdir(tmp_dir)
            shutil.copy(self.source_path, '.')  # Fixme: symlink
            # Run LaTeX to generate PDF
            command = (
                self.LATEX_COMMAND,
                '-shell-escape',
                '-interaction=batchmode',
                # '-output-directory=' + tmp_dir,
                str(self.source_path.name),
            )
            subprocess.check_call(command, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
            # Fixme: pdf2svg not installed
            # Class standalone Warning: Conversion failed!
            shutil.copy(self.path, self.absolut_path)
            os.chdir(current_dir)
