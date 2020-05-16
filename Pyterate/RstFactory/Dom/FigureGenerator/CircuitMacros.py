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

from pathlib import Path
import logging
import os
import subprocess
import shutil
import tempfile

from ..FigureMarkups import ExternalFigureNode

####################################################################################################

CIRCUIT_MACROS_PATH = Path.home().joinpath('texmf', 'Circuit_macros')

####################################################################################################

_module_logger = logging.getLogger(__name__)

####################################################################################################

class CircuitMacrosNode(ExternalFigureNode):

    """ This class represents an image block for a circuit macros figure. """

    COMMAND = 'circuit_macros'

    _logger = _module_logger.getChild('CircuitMacrosImage')

    ##############################################

    def __init__(self, document, m4_filename, **kwargs):

        figure_path = m4_filename.replace('.m4', '.png')
        source_path = document.topic.join_path('m4', m4_filename) # Fixme: m4 directory ???

        super().__init__(document, source_path, figure_path, **kwargs)

    ##############################################

    def make_figure(self):

        self._logger.info('\nMake circuit macros figure {}'.format(self.source_path))
        try:
            self._make_figure()
        except subprocess.CalledProcessError:
            self._logger.error("Failed to make circuit macros figure", self.source_path)

    ##############################################

    def _make_figure(self,
                  # density=300,
                  # transparent='white',
                  circuit_macros_path=CIRCUIT_MACROS_PATH):

        dst_path = self.document.topic_rst_path

        # Create a temporary directory, it is automatically deleted
        tmp_dir = tempfile.TemporaryDirectory()
        self._logger.info('Temporary directory ' + tmp_dir.name)

        dev_null = open(os.devnull, 'w')

        # Generate LaTeX file

        picture_tex_path = Path(tmp_dir.name).joinpath('picture.tex')

        picture_tex_header = r'''
    \documentclass[11pt]{article}
    \usepackage{tikz}
    \usetikzlibrary{external}
    \tikzexternalize
    \pagestyle{empty}
    \begin{document}
'''

        with open(picture_tex_path, 'w') as f:
            f.write(picture_tex_header)

            # Run dpic in pgf mode
            m4_command = (
                'm4',
                '-I' + str(circuit_macros_path),
                'pgf.m4',
                'libcct.m4',
                self.source_path,
            )
            dpic_command = ('dpic', '-g')

            m4_process = subprocess.Popen(m4_command,
                                          #shell=True,
                                          stdout=subprocess.PIPE)
            dpic_process = subprocess.Popen(dpic_command,
                                            #shell=True,
                                            stdin=m4_process.stdout,
                                            stdout=subprocess.PIPE)
            m4_process.stdout.close()
            dpic_rc = dpic_process.wait()
            if dpic_rc:
                raise subprocess.CalledProcessError(dpic_rc, 'dpic')
            dpic_output = dpic_process.stdout.read().decode('utf-8')
            f.write(dpic_output)
            f.write(r'\end{document}')

        # Run LaTeX to generate PDF

        current_dir = os.curdir
        os.chdir(tmp_dir.name)
        latex_command = (
            'pdflatex',
            '-shell-escape',
            # '-output-directory=' + tmp_dir.name,
            'picture.tex',
        )
        subprocess.check_call(latex_command, stdout=dev_null, stderr=subprocess.STDOUT)

        os.chdir(current_dir)
        basename = self.source_path.stem
        pdf_path = dst_path.joinpath(basename + '.pdf')
        png_path = dst_path.joinpath(basename + '.png')

        self._logger.info('Generate {}'.format(png_path))
        # print('Generate ' + png_path)
        shutil.copy(Path(tmp_dir.name).joinpath('picture-figure0.pdf'), pdf_path)

        # Convert PDF to PNG

        # subprocess.check_call(('convert',
        #                        '-density', str(density),
        #                        '-transparent', str(transparent),
        #                        pdf_path, png_path),
        #                       stdout=dev_null, stderr=subprocess.STDOUT)

        mutool_command = (
            'mutool',
            'convert',
            '-A', '8',
            '-O', 'resolution=300', # ,colorspace=rgb,alpha
            '-F', 'png',
            '-o', str(png_path),
            str(pdf_path),
            '1'
        )
        subprocess.check_call(mutool_command, stdout=dev_null, stderr=subprocess.STDOUT)
        output_png_path = png_path.parent.joinpath(png_path.stem + '1.png')
        output_png_path.rename(png_path)
