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
import tempfile

from ..Jupyter import JupyterClient
from ..Template import TemplateAggregator
from ..Tools.Path import remove_extension
from ..Tools.Timestamp import timestamp
from .Dom import *

# Load default extensions
from .FigureGenerator.Registry import ExtensionMetaclass

####################################################################################################

_module_logger = logging.getLogger(__name__)

####################################################################################################

SETUP_CODE = '''
from Pyterate.RstFactory.Tools import save_figure
'''

####################################################################################################

class Document:

    """ This class is responsible to process an document. """

    _logger = _module_logger.getChild('Document')

    FIGURE_MARKUPS = ['fig', 'lfig', 'i', 'itxt', 'o']
    FIGURE_MARKUPS += ExtensionMetaclass.extension_markups()

    ##############################################

    def __init__(self, topic, filename):

        self._topic = topic
        self._basename = remove_extension(filename) # input basename

        path = topic.join_path(filename)
        self._is_link = os.path.islink(path)
        self._path = os.path.realpath(path) # input path

        if self._is_link:
            factory = self.factory
            path = factory.join_rst_document_path(os.path.relpath(self._path, factory.documents_path))
            self._rst_path = remove_extension(path) + '.rst'
        else:
            self._rst_path = self._topic.join_rst_path(self.rst_filename)

    ##############################################

    @property
    def topic(self):
        return self._topic

    @property
    def factory(self):
        return self._topic.factory

    @property
    def path(self):
        return self._path

    @property
    def basename(self):
        return self._basename

    @property
    def rst_filename(self):
        return self._basename + '.rst'

    @property
    def rst_inner_path(self):
        return os.path.sep + os.path.relpath(self._rst_path, self.factory.rst_source_path)

    ##############################################

    @property
    def is_link(self):
        return self._is_link

    ##############################################

    def read(self):

        # Fixme: API ??? called process_document()

        # Must be called first !

        with open(self._path) as fh:
            self._source = fh.readlines()
        self._parse_source()

    ##############################################

    @property
    def source_timestamp(self):
        return timestamp(self._path)

    ##############################################

    @property
    def rst_timestamp(self):

        if os.path.exists(self._rst_path):
            return timestamp(self._rst_path)
        else:
            return -1

    ##############################################

    def __bool__(self):
        """Return True if source is older than rst."""
        return self.source_timestamp > self.rst_timestamp

    ##############################################

    def run_code(self):

        self._logger.info("\nRun document " + self._path)

        with tempfile.TemporaryDirectory() as working_directory:
            jupyter_client = JupyterClient(working_directory)
            jupyter_client.run_cell(SETUP_CODE)
            for chunk in self._dom.iter_on_code_chunks():
                code = chunk.to_python()
                self._logger.debug('Execute\n{}'.format(code))
                outputs = jupyter_client.run_cell(code)
                if outputs:
                    output = outputs[0]
                    self._logger.debug('Output {0.output_type}\n{0}'.format(output))
                    chunk.outputs = outputs

###    def run_code(self):
###
###        """This function make a temporary copy of the document with calls to *save_figure* and run it.
###
###        """
###
###        working_directory = os.path.dirname(self._path)
###
###        tmp_file = tempfile.NamedTemporaryFile(dir=working_directory,
###                                               prefix='__document_rst_factory__', suffix='.py', mode='w')
###        tmp_file.write('from Pyterate.RstFactory.Document import save_figure\n')
###        tmp_file.write('from Pyterate.RstFactory import Document as DocumentModule\n')
###        tmp_file.write('DocumentModule.FIGURE_DIRECTORY = "{}"\n'.format(self._topic.rst_path))
###        tmp_file.write('\n')
###        for chunck in self._dom:
###            if isinstance(chunck, (CodeChunk, FigureChunk, OutputChunk, RstFormatChunk)):
###                tmp_file.write(chunck.to_python())
###        tmp_file.flush()
###
###        self._logger.info("\nRun document " + self._path)
###        # with open(tmp_file.name, 'r') as fh:
###        #     print(fh.read())
###        with open(self.stdout_path, 'w') as stdout:
###            with open(self.stderr_path, 'w') as stderr:
###                env = dict(os.environ)
###                env['PyterateLogLevel'] = 'WARNING'
###                process = subprocess.Popen((sys.executable, tmp_file.name),
###                                           stdout=stdout,
###                                           stderr=stderr,
###                                           cwd=working_directory,
###                                           env=env)
###                rc = process.wait()
###                if rc:
###                    self._logger.error("Failed to run document " + self._path)
###                    self.factory.register_failure(self)

    ##############################################

    def make_external_figure(self, force):

        for chunck in self._dom:
            if isinstance(chunck, ExtensionMetaclass.extensions()):
                if force or chunck:
                    chunck.make_figure()

    ##############################################

    def _append_rst_chunck(self):

        # if self._rst_chunck:
        chunk = self._rst_chunck
        if chunk.has_format():
            chunk = chunk.to_rst_format_chunk()
        self._dom.append(chunk)
        self._rst_chunck = RstChunk()

    ##############################################

    def _append_code_chunck(self, hidden=False):

        if self._code_chunck:
            self._dom.append(self._code_chunck)
        if hidden:
            self._code_chunck = HiddenCodeChunk()
        else:
            self._code_chunck = CodeChunk()

    ##############################################

    def _line_start_by_markup(self, line, markup):

        return line.startswith('#{}#'.format(markup))

    ##############################################

    def _line_starts_by_figure_markup(self, line):

        for markup in self.FIGURE_MARKUPS:
            if self._line_start_by_markup(line, markup):
                return True
        return False

    ##############################################

    def _parse_source(self):

        """Parse the Python source code and extract chunks of codes, RST contents, plot and Tikz figures.
        The source code is annoted using comment lines starting with special directives of the form
        *#directive name#*.  RST content lines start with *#!#*.  We can include a figure using
        *#lfig#*, a figure generated by matplotlib using the directive *#fig#*, tikz figure using
        *#tz#* and the content of a file using *#itxt#* and *#i#* for Python source.  Comment that
        must be skipped start with *#?#*.  Hidden Python code start with *#h#*.  The directive *#o#*
        is used to split the output and to instruct to include the previous chunk.  RST content can
        be formatted with variable from the locals dictionary using *@<@...@>@* instead of *{...}*.

        """

        self._dom = Dom()
        self._rst_chunck = RstChunk()
        self._code_chunck = CodeChunk()

        # Use a while loop trick to remove consecutive blank lines
        number_of_lines = len(self._source)
        i = 0
        while i < number_of_lines:
            line = self._source[i]
            i += 1
            remove_next_blanck_line = True
            if (self._line_start_by_markup(line, '?')
                or line.startswith('#'*10) # long rule # Fixme: hardcoded !
                or line.startswith(' '*4 + '#'*10)): # short rule
                pass # these comments
            elif self._line_starts_by_figure_markup(line):
                if self._rst_chunck:
                    self._append_rst_chunck()
                elif self._code_chunck:
                    self._append_code_chunck()
                # Fixme: use generic map ?
                if self._line_start_by_markup(line, 'fig'):
                    self._dom.append(FigureChunk(self, line))
                elif self._line_start_by_markup(line, 'lfig'):
                    self._dom.append(LocaleFigureChunk(line, self._topic.path, self._topic.rst_path))
                elif self._line_start_by_markup(line, 'i'):
                    self._dom.append(PythonIncludeChunk(self, line))
                elif self._line_start_by_markup(line, 'itxt'):
                    self._dom.append(LitteralIncludeChunk(self, line))
                elif self._line_start_by_markup(line, 'o'):
                    if not self._dom.last_chunk.is_executed:
                        self._logger.error('Previous chunk must be code') # Fixme: handle
                    self._dom.append(OutputChunk(self._dom.last_chunk))
                else:
                    for markup, cls in ExtensionMetaclass.iter():
                        if self._line_start_by_markup(line, markup):
                            self._dom.append(cls(line, self._topic.path, self._topic.rst_path))
                            break
            elif self._line_start_by_markup(line, '!'): # RST content
                if self._code_chunck:
                    self._append_code_chunck()
                self._rst_chunck.append(line.strip()[4:] + '\n') # hack to get blank line
            else: # Python code
                # if line.startswith('pylab.show()'):
                #     continue
                remove_next_blanck_line = False
                if self._rst_chunck:
                    self._append_rst_chunck()
                if self._line_start_by_markup(line, 'h') and isinstance(self._code_chunck, CodeChunk):
                    self._append_code_chunck(True)
                elif isinstance(self._code_chunck, HiddenCodeChunk):
                    self._append_code_chunck(False)
                self._code_chunck.append(line)
            if remove_next_blanck_line and i < number_of_lines and not self._source[i].strip():
                i += 1
        if self._rst_chunck:
            self._append_rst_chunck()
        elif self._code_chunck:
            self._append_code_chunck()

    ##############################################

    def _has_title(self):

        """Return whether a title is defined."""

        # Fixme: test if first chunck ?
        for chunck in self._dom:
            if isinstance(chunck, RstChunk):
                content = str(chunck)
                if '='*(3+2) in content: # Fixme: hardcoded !
                    return True

        return False

    ##############################################

    def make_rst(self):

        """ Generate the document RST file. """

        self._logger.info("\nCreate RST file " + self._rst_path)

        ### self._read_output_chunk()

        # place the Python file in the rst path
        python_file_name = self._basename + '.py'
        link_path = self._topic.join_rst_path(python_file_name)
        if not os.path.exists(link_path):
            os.symlink(self._path, link_path)

        kwargs = {
            'python_file':python_file_name,
        }

        has_title = self._has_title()
        if not has_title:
            kwargs['title'] = self._basename.replace('-', ' ').title() # Fixme: Capitalize of

        template_aggregator = TemplateAggregator(self.factory.template_environment)
        template_aggregator.append('document', **kwargs)

        with open(self._rst_path, 'w') as fh:
            fh.write(str(template_aggregator))
            for chunck in self._dom:
                fh.write(str(chunck))
            # fh.write(self._output)
