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

"""This module implements a RST files generator for documents.

"""

####################################################################################################

import logging
import os

from .Topic import Topic

####################################################################################################

_module_logger = logging.getLogger(__name__)

####################################################################################################

class RstFactory:

    """This class processes recursively the documents directory and generate figures and RST files.

    """

    _logger = _module_logger.getChild('RstFactory')

    ##############################################

    def __init__(self, documents_path, rst_source_path, rst_directory,
                 show_counter=False):

        """
        Parameters:

        documents_path: string
            path of the documents

        rst_source_path: string
            path of the RST source directory

        rst_directory: string
            relative path of the documents in the RST sources

        show_counter: Boolean
            show documents counters in toc
        """

        # Fixme: handle ~
        self._documents_path = os.path.realpath(documents_path)

        self._rst_source_path = os.path.realpath(rst_source_path)
        self._rst_directory = os.path.join(self._rst_source_path, rst_directory) # Fixme: name ?
        if not os.path.exists(self._rst_directory):
            os.makedirs(self._rst_directory)

        self._logger.info("\nDocuments Path: " + self._documents_path)
        self._logger.info("\nRST Path: " + self._rst_directory)

        self._show_counter = show_counter

        self._topics = {}
        self._document_failures = []

    ##############################################

    @property
    def documents_path(self):
        return self._documents_path

    @property
    def rst_source_path(self):
        return self._rst_source_path

    @property
    def rst_directory(self):
        return self._rst_directory

    @property
    def show_counter(self):
        return self._show_counter

    @property
    def topics(self):
        return self._topics

    ##############################################

    # Fixme: name ?

    def join_documents_path(self, *args):
        return os.path.join(self._documents_path, *args)

    def join_rst_document_path(self, *args):
        return os.path.join(self._rst_directory, *args)

    ##############################################

    def register_failure(self, document):
        self._document_failures.append(document)

    ##############################################

    def _process_topic(self, topic_path, kwargs):

        relative_topic_path = os.path.relpath(topic_path, self._documents_path)
        if relative_topic_path == '.':
            relative_topic_path = ''

        # Fixme: kwargs handling
        make_external_figure = kwargs.get('make_external_figure', False)

        topic = Topic(self, relative_topic_path)
        self._topics[relative_topic_path] = topic # collect topics

        topic.process_documents(**kwargs)
        topic.make_toc(make_external_figure)

    ##############################################

    def process_recursively(self, **kwargs):

        """Process recursively the documents directory.

        kwargs: `make_figure`, `make_external_figure`, `force`

        """

        # walk top down so as to generate the subtopics first
        self._topics.clear()
        for topic_path, _, _ in os.walk(self._documents_path, topdown=False, followlinks=True):
            self._process_topic(topic_path, kwargs)

        if self._document_failures:
            self._logger.warning(
                "These documents failed:\n" +
                '\n'.join([document.path for document in self._document_failures]))
