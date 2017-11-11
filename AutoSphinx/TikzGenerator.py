####################################################################################################
#
# AutoSphinx - Sphinx add-ons to create API documentation for Python projects
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

# import logging
import os
import subprocess
import shutil
import tempfile

####################################################################################################

# _module_logger = logging.getLogger(__name__)

####################################################################################################

LATEX_COMMAND = 'pdflatex'
# LATEX_COMMAND = 'lualatex'

####################################################################################################

def generate(tex_path, dst_path):

    with tempfile.TemporaryDirectory() as tmp_dir:
        # _module_logger.info('Temporary directory ' + tmp_dir)

        # current_dir = os.curdir
        os.chdir(tmp_dir)
        shutil.copy(tex_path, '.')

        # Run LaTeX to generate PDF
        command = (
            LATEX_COMMAND,
            '-shell-escape',
            '-interaction=batchmode',
            # '-output-directory=' + tmp_dir,
            os.path.basename(tex_path),
        )
        dev_null = open(os.devnull, 'w')
        subprocess.check_call(command, stdout=dev_null, stderr=subprocess.STDOUT)

        basename = os.path.splitext(os.path.basename(tex_path))[0]
        svg_basename = basename + '.svg'
        svg_path = os.path.join(dst_path, svg_basename)
        shutil.copy(svg_basename, svg_path)
