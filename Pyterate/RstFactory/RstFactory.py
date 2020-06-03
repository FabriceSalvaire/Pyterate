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

from pathlib import Path
import json
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

    def __init__(self, settings):

        """
        Parameters:

        settings:
            :class:`RstFactory.Settings.DefaultRstFactorySettings` instance

        """

        self._settings = settings

        if self._settings.make_rst:
            os.makedirs(self._settings.rst_path, exist_ok=True)

        self._topics = {}
        self._document_failures = []

        self._load_failure()

    ##############################################

    def _load_failure(self):
        json_path = self._settings.failure_path
        if json_path.exists():
            with open(json_path, 'r') as fh:
                self._failures = json.load(fh)
                self._logger.warning('loaded failures from {}'.format(json_path))
        else:
            self._failures = []

    ##############################################

    @property
    def settings(self):
        return self._settings

    @property
    def topics(self):
        return self._topics

    ##############################################

    def was_failure(self, document):
        return str(document.path) in self._failures

    def register_failure(self, document):
        self._document_failures.append(document)

    @property
    def has_failure(self):
        return bool(self._document_failures)

    ##############################################

    def _process_topic(self, topic_path):

        relative_topic_path = self._settings.relative_input_path(topic_path)

        topic = Topic(self, relative_topic_path)
        self._topics[relative_topic_path] = topic # collect topics

        topic.process_documents()
        if self._settings.make_rst:
            topic.make_toc()

    ##############################################

    def process_recursively(self):

        """Process recursively the documents directory."""

        # walk top down so as to generate the subtopics first
        self._topics.clear()
        for topic_path, _, _ in os.walk(self._settings.input_path, topdown=False, followlinks=True):
            self._process_topic(Path(topic_path))

        self._logger.info('Done')

        failure_path = self._settings.failure_path
        if self.has_failure:
            documents = [str(document.path) for document in self._document_failures]
            self._logger.warning('These documents failed:\n' + '\n'.join(documents))

            with open(failure_path, 'w') as fh:
                json.dump(documents, fh, indent=4)
                self._logger.warning('Dumped failures in {}'.format(failure_path))
            return False
        else:
            self._logger.info('Here')
            failure_path.unlink(missing_ok=True)
            return True
