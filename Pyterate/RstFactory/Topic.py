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

""" This module implements a RST files generator for documents.
"""

####################################################################################################

import glob
import logging
import os

from ..Template import TemplateAggregator
from .Document import Document

####################################################################################################

_module_logger = logging.getLogger(__name__)

####################################################################################################

class Topic:

    _logger = _module_logger.getChild('Topic')

    EXCLUDED_FILES = (
        # these file should be flymake temporary file
        'flymake_',
        'flycheck_',
    )

    SKIP_PATTERN = '#skip#'
    IMAGE_DIRECTIVE = '.. image:: '
    IMAGE_DIRECTIVE_LENGTH = len(IMAGE_DIRECTIVE)

    ##############################################

    def __init__(self, factory, relative_path):

        self._factory = factory
        self._relative_path = relative_path # relative input path
        self._basename = os.path.basename(relative_path) # topic directory

        self._path = self._factory.join_documents_path(relative_path) # input path
        self._rst_path = self._factory.join_rst_document_path(relative_path) # output path

        self._subtopics = [] # self._retrieve_subtopics()
        self._documents = []
        self._links = []

        python_files = list(self._python_files_iterator()) # Fixme: better ?
        if python_files:
            self._logger.info("\nProcess Topic: " + relative_path)
            os.makedirs(self._rst_path) # removed code
            for filename in python_files:
                document = Document(self, filename)
                if document.is_link:
                    self._logger.info("\n  found link: " + filename)
                    self._links.append(document)
                else:
                    self._logger.info("\n  found: " + filename)
                    self._documents.append(document)

    ##############################################

    def __bool__(self):
        # Fixme: usage ???
        return os.path.exists(self._rst_path)
        # return bool(self._documents) or bool(self._links)

    ##############################################

    @property
    def factory(self):
        return self._factory

    @property
    def basename(self):
        return self._basename

    @property
    def path(self):
        return self._path

    @property
    def rst_path(self):
        return self._rst_path

    ##############################################

    def join_path(self, filename):
        return os.path.join(self._path, filename)

    def join_rst_path(self, filename):
        return os.path.join(self._rst_path, filename)

    ##############################################

    def _files_iterator(self, extension, file_filter):

        pattern = os.path.join(self._path, '*.' + extension)
        for file_path in glob.glob(pattern):
            if file_filter(file_path):
                yield os.path.basename(file_path) # relative path

    ##############################################

    def _is_file_skipped(self, filename):

        absolut_path = os.path.join(self._path, filename)
        with open(absolut_path, 'r') as fh:
            first_line = fh.readline()
            second_line = fh.readline()

        return not (first_line.startswith(self.SKIP_PATTERN) or
                    second_line.startswith(self.SKIP_PATTERN))

    ##############################################

    def _filter_python_files(self, filename):

        if filename.endswith('.py'):
            for pattern in self.EXCLUDED_FILES:
                if filename.startswith(pattern):
                    return False
            return self._is_file_skipped(filename)
        else:
            return False

    ##############################################

    def _python_files_iterator(self):
        return self._files_iterator('py', self._filter_python_files)

    ##############################################

    def _readme_path(self):
        return self.join_path('readme.rst') # Fixme: hardcoded filename !

    ##############################################

    def _has_readme(self):
        return os.path.exists(self._readme_path())

    ##############################################

    def _read_readme(self):

        """Read readme and collect figures"""

        figures = []
        with open(self._readme_path()) as fh:
            content = fh.read()
            for line in content.split('\n'):
                if line.startswith(self.IMAGE_DIRECTIVE):
                    figure = line[self.IMAGE_DIRECTIVE_LENGTH:]
                    figures.append(figure)

        return content, figures

    ##############################################

    def process_documents(self, **kwargs):

        for document in self._documents:
            self.process_document(document, **kwargs)

    ##############################################

    def process_document(self, document, make_figure=True, make_external_figure=True, force=False):

        # Fixme: kwargs

        document.read()
        if force or document:
            if make_figure:
                document.make_figure()
            document.make_rst()
        if make_external_figure:
            document.make_external_figure(force)

    ##############################################

    def _directory_iterator(self):

        for filename in os.listdir(self._rst_path):
            path = self.join_rst_path(filename)
            if os.path.isdir(path):
                yield path # absolut path

    ##############################################

    def _subtopic_iterator(self):

        for path in self._directory_iterator():
            if os.path.exists(os.path.join(path, 'index.rst')): # Fixme: hardcoded filename !
                relative_path = os.path.relpath(path, self._factory.rst_directory)
                topic = self._factory.topics[relative_path]
                yield topic

    ##############################################

    def _retrieve_subtopics(self):

        # Fixme: ???
        if not self:
            return None

        self._subtopics = list(self._subtopic_iterator())

    ##############################################

    def make_toc(self, make_external_figure):

        """ Create the TOC. """

        # Fixme: ???
        if not self:
            return

        toc_path = self.join_rst_path('index.rst')
        self._logger.info("\nCreate TOC " + toc_path)

        kwargs = {}

        if self._has_readme():
            readme_content, figures = self._read_readme()
            kwargs['user_content'] = readme_content
            # Fixme: external figure in readme / check PySpice code
            # if make_external_figure:
            #   ...
        else:
            kwargs['title'] = self._basename.replace('-', ' ').title() # Fixme: Capitalize of

        # Sort the TOC
        # Fixme: sometimes we want a particular order !
        file_dict = {document.basename:document.rst_filename for document in self._documents}
        file_dict.update({link.basename:link.rst_inner_path for link in self._links})
        kwargs['toc_items'] = [file_dict[x] for x in sorted(file_dict.keys())]

        self._retrieve_subtopics()
        subtopics = [topic.basename for topic in self._subtopics]
        kwargs['subtopics'] = sorted(subtopics)

        if self._factory.show_counter:
            self._number_of_documents = len(self._documents) # don't count links twice
            kwargs['number_of_links'] = len(self._links)
            kwargs['number_of_subtopics'] = len(self._subtopics)
            number_of_subtopics = sum([topic._number_of_documents for topic in self._subtopics])
            kwargs['number_of_documents'] = self._number_of_documents + number_of_subtopics

        template_aggregator = TemplateAggregator(self._factory.template_environment)
        template_aggregator.append('toc', **kwargs)

        with open(toc_path, 'w') as fh:
            fh.write(str(template_aggregator))
