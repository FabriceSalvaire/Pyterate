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

""" This module implements a RST files generator for examples.
"""

####################################################################################################

import logging
import os

from .Topic import Topic

####################################################################################################

_module_logger = logging.getLogger(__name__)

####################################################################################################

class RstFactory:

    """This class processes recursively the examples directory and generate figures and RST files."""

    _logger = _module_logger.getChild('RstFactory')

    ##############################################

    def __init__(self, examples_path, rst_source_directory, rst_example_directory,
                 show_counter=False):

        """
        Parameters:

        examples_path: string
            path of the examples

        rst_source_directory: string
            path of the RST source directory

        rst_example_directory: string
            relative path of the examples in the RST sources

        show_counter: Boolean
            show examples counters in toc
        """

        self._examples_path = os.path.realpath(examples_path)

        self._rst_source_directory = os.path.realpath(rst_source_directory)
        self._rst_example_directory = os.path.join(self._rst_source_directory, rst_example_directory)
        if not os.path.exists(self._rst_example_directory):
            os.mkdir(self._rst_example_directory)

        self._show_counter = show_counter

        self._topics = {}

        self._logger.info("\nExamples Path: " + self._examples_path)
        self._logger.info("\nRST Path: " + self._rst_example_directory)

        self._example_failures = []

    ##############################################

    @property
    def examples_path(self):
        return self._examples_path

    @property
    def rst_source_directory(self):
        return self._rst_source_directory

    @property
    def rst_example_directory(self):
        return self._rst_example_directory

    @property
    def show_counter(self):
        return self._show_counter

    @property
    def topics(self):
        return self._topics

    ##############################################

    def join_examples_path(self, *args):
        return os.path.join(self._examples_path, *args)

    def join_rst_example_path(self, *args):
        return os.path.join(self._rst_example_directory, *args)

    ##############################################

    def process_recursively(self, make_figure=True, make_external_figure=True, force=False):

        """ Process recursively the examples directory. """

        # walk top down so as to generate the subtopics first
        self._topics.clear()
        for current_path, sub_directories, files in os.walk(self._examples_path,
                                                            topdown=False,
                                                            followlinks=True):
            relative_current_path = os.path.relpath(current_path, self._examples_path)
            if relative_current_path == '.':
                relative_current_path = ''
            topic = Topic(self, relative_current_path)
            self._topics[relative_current_path] = topic # collect the topics
            topic.process_examples(make_figure, make_external_figure, force)
            topic.make_toc(make_external_figure)

        if self._example_failures:
            self._logger.warning("These examples failed:\n" +
                                 '\n'.join([example.path for example in self._example_failures]))

    ##############################################

    def register_failure(self, example):

        self._example_failures.append(example)
