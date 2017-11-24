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
import sys
import tempfile

from .Dom import *
from .Template import *
from .Tools import timestamp

# Load default extensions
from .FigureGenerator.Registry import ExtensionMetaclass

####################################################################################################

_module_logger = logging.getLogger(__name__)

####################################################################################################

FIGURE_DIRECTORY = None

####################################################################################################

def remove_extension(filename):
    return os.path.splitext(filename)[0]

def file_extension(filename):
    return os.path.splitext(filename)[1]

####################################################################################################

def save_figure(figure,
                figure_filename):

    """ This function is called from document to save a figure. """

    figure_format = file_extension(figure_filename)[1:] # foo.png -> png
    figure_path = os.path.join(FIGURE_DIRECTORY, figure_filename)
    _module_logger.info("\nSave figure " + figure_path)
    figure.savefig(figure_path,
                   format=figure_format,
                   dpi=150,
                   orientation='landscape', papertype='a4',
                   transparent=True, frameon=False,
    )

####################################################################################################

class Document:

    """ This class is responsible to process an document. """

    _logger = _module_logger.getChild('Document')

    ##############################################

    def __init__(self, topic, filename):

        self.__figure_markups__ = ['fig', 'lfig', 'i', 'itxt', 'o']
        self.__figure_markups__ += ExtensionMetaclass.extension_markups()

        self._topic = topic
        self._basename = remove_extension(filename)

        path = topic.join_path(filename)
        self._is_link = os.path.islink(path)
        self._path = os.path.realpath(path)

        if self._is_link:
            factory = self._topic.factory
            path = factory.join_rst_document_path(os.path.relpath(self._path, factory.documents_path))
            self._rst_path = remove_extension(path) + '.rst'
        else:
            self._rst_path = self._topic.join_rst_path(self.rst_filename)

        self._stdout = None

        self._stdout_chunck_counter = -1

    ##############################################

    @property
    def topic(self):
        return self._topic

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
        return os.path.sep + os.path.relpath(self._rst_path, self._topic.factory.rst_source_path)

    @property
    def stdout_path(self):
        # return remove_extension(self._rst_path) + '.stdout'
        return self._topic.join_rst_path(self._basename + '.stdout')

    @property
    def stderr_path(self):
        # return remove_extension(self._rst_path) + '.stdout'
        return self._topic.join_rst_path(self._basename + '.stderr')

    ##############################################

    def increment_stdout_chunk_counter(self):
        self._stdout_chunck_counter += 1
        return self._stdout_chunck_counter

    def stdout_chunk(self, i):
        return self._stdout_chunks[i]

    ##############################################

    @property
    def is_link(self):
        return self._is_link

    ##############################################

    def read(self):

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

        return self.source_timestamp > self.rst_timestamp

    ##############################################

    def make_figure(self):

        """This function make a temporary copy of the document with calls to *save_figure* and run it.

        """

        working_directory = os.path.dirname(self._path)

        tmp_file = tempfile.NamedTemporaryFile(dir=working_directory,
                                               prefix='__document_rst_factory__', suffix='.py', mode='w')
        tmp_file.write('from Pyterate.RstFactory.Document import save_figure\n')
        tmp_file.write('from Pyterate.RstFactory import Document as DocumentModule\n')
        tmp_file.write('DocumentModule.FIGURE_DIRECTORY = "{}"\n'.format(self._topic.rst_path))
        tmp_file.write('\n')
        for chunck in self._dom:
            if isinstance(chunck, (CodeChunk, FigureChunk, OutputChunk, RstFormatChunk)):
                tmp_file.write(chunck.to_python())
        tmp_file.flush()

        self._logger.info("\nRun document " + self._path)
        # with open(tmp_file.name, 'r') as fh:
        #     print(fh.read())
        with open(self.stdout_path, 'w') as stdout:
            with open(self.stderr_path, 'w') as stderr:
                env = dict(os.environ)
                env['PyterateLogLevel'] = 'WARNING'
                process = subprocess.Popen((sys.executable, tmp_file.name),
                                           stdout=stdout,
                                           stderr=stderr,
                                           cwd=working_directory,
                                           env=env)
                rc = process.wait()
                if rc:
                    self._logger.error("Failed to run document " + self._path)
                    self._topic.factory.register_failure(self)

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
            chunk = chunk.to_rst_format_chunk(self, self.increment_stdout_chunk_counter())
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

        for markup in self.__figure_markups__:
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
                or line.startswith('#'*10)
                or line.startswith(' '*4 + '#'*10)):
                pass # these comments
            elif self._line_starts_by_figure_markup(line):
                if self._rst_chunck:
                    self._append_rst_chunck()
                elif self._code_chunck:
                    self._append_code_chunck()
                # Fixme: use generic map ?
                if self._line_start_by_markup(line, 'fig'):
                    self._dom.append(FigureChunk(line))
                elif self._line_start_by_markup(line, 'lfig'):
                    self._dom.append(LocaleFigureChunk(line, self._topic.path, self._topic.rst_path))
                elif self._line_start_by_markup(line, 'i'):
                    self._dom.append(PythonIncludeChunk(self, line))
                elif self._line_start_by_markup(line, 'itxt'):
                    self._dom.append(LitteralIncludeChunk(self, line))
                elif self._line_start_by_markup(line, 'o'):
                    self._dom.append(OutputChunk(self, line, self.increment_stdout_chunk_counter()))
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

    def _read_output_chunk(self):

        # Read the stdout and split in chunck
        with open(self.stdout_path) as fh:
            self._stdout = fh.read()
        self._stdout_chunks = []
        start = 0
        last_i = -1
        lines = self._stdout.split('\n')
        for i, line in enumerate(lines): # Fixme: portability
            if line.startswith('\f'):
                slice_ = slice(start, i)
                self._stdout_chunks.append((slice_, '\n'.join(lines[slice_])))
                start = i + 1
            last_i = i
        # Fixme: add last empty line ?
        if start <= last_i:
            slice_ = slice(start, last_i +1)
            self._stdout_chunks.append((slice_, '\n'.join(lines[slice_])))

    ##############################################

    def make_rst(self):

        """ Generate the document RST file. """

        self._logger.info("\nCreate RST file " + self._rst_path)

        self._read_output_chunk()

        has_title= False
        for chunck in self._dom:
            # self._logger.info('Chunck {0.__class__.__name__}'.format(chunck))
            if isinstance(chunck, RstChunk):
                content = str(chunck)
                if '='*7 in content:
                    has_title = True
                break

        if not has_title:
            # Fixme: duplicated code
            title = self._basename.replace('-', ' ').title() # Fixme: Capitalize of
            title_line = '='*(len(title)+2)
            header = TITLE_TEMPLATE.format(title=title, title_line=title_line)
        else:
            header = ''

        # place the Python file in the rst path
        python_file_name = self._basename + '.py'
        link_path = self._topic.join_rst_path(python_file_name)
        if not os.path.exists(link_path):
            os.symlink(self._path, link_path)

        with open(self._rst_path, 'w') as fh:
            fh.write(INCLUDES_TEMPLATE)
            if not has_title:
                fh.write(header)
            fh.write(GET_CODE_TEMPLATE.format(filename=python_file_name))
            for chunck in self._dom:
                fh.write(str(chunck))

            # fh.write(self._output)
