####################################################################################################
#
# Pyterate - Sphinx add-ons to create API documentation for Python projects
# Copyright (C) 2017 Salvaire Fabrice
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

"""This module provides a tool similar to `sphinx-apidoc
<http://www.sphinx-doc.org/en/master/man/sphinx-apidoc.html>`_ to generate automatically the Sphinx
sources for an API documentation using the `autodoc extension
<http://www.sphinx-doc.org/en/master/ext/autodoc.html>`_.

In comparison to *sphinx-apidoc*, it generates sorter titles.

.. a tool for automatic generation of Sphinx sources using the autodoc extension.

.. See http://www.sphinx-doc.org/en/stable/ext/autodoc.html for further information on Sphinx
.. autodoc extension.

"""

####################################################################################################

import logging
import os

from ..Template import TemplateEnvironment

####################################################################################################

_module_logger = logging.getLogger(__name__)

####################################################################################################

# For default set autodoc_default_flags in conf.py
#
# :members:           include members
# :undoc-members:     include members without docstrings
# :private-members:   include private
# :special-members:   include __special__
# :inherited-members: include inherited members
# :no-undoc-members:

####################################################################################################

class ApiRstFactory:

    """This class build recursively a Sphinx API documentation from a Python root module."""

    INIT_FILE_NAME = '__init__.py'

    _logger = _module_logger.getChild('ApiRstFactory')

    ##############################################

    def __init__(self, module_path, rst_directory, excluded_directory):

        self._rst_directory = os.path.realpath(rst_directory)
        self._root_module_path = os.path.realpath(module_path)

        self._excluded_directory = [os.path.join(self._root_module_path, x)
                                    for x in excluded_directory]
        self._root_module_name = os.path.basename(self._root_module_path)

        self._logger.info('RST API Path:     {}'.format(self._rst_directory))
        self._logger.info('Root Module Path: {}'.format(self._root_module_path))
        self._logger.info('Root Module Name: {}'.format(self._root_module_name))
        self._logger.info('Exclude:' + '\n  '.join(self._excluded_directory))

        template_path = os.path.join(os.path.dirname(__file__), 'templates') # Fixme: custom
        self._template_environment = TemplateEnvironment(template_path)

        if not os.path.exists(self._rst_directory):
            os.makedirs(self._rst_directory)

        self._process_recursively()

    ##############################################

    def _process_recursively(self):

        """ Process recursively the inner Python files and directories. """

        for module_path, sub_directories, files in os.walk(self._root_module_path, followlinks=True):

            if module_path in self._excluded_directory:
                continue

            sub_directories = [
                sub_directory
                for sub_directory in sub_directories
                if (os.path.join(module_path, sub_directory) not in self._excluded_directory
                    and sub_directory != '__pycache__')
            ]

            if self.is_python_directory_module(module_path):
                python_files = [
                    file_name
                    for file_name in files
                    if self.is_python_file(file_name)
                ]
                sub_modules = [
                    sub_directory
                    for sub_directory in sub_directories
                    if self.is_python_directory_module(os.path.join(module_path, sub_directory))
                ]
                self._process_directory_module(module_path, sorted(python_files), sorted(sub_modules))

    ##############################################

    def _process_directory_module(self, module_path, python_files, sub_modules):

        directory_module_name = os.path.basename(module_path)
        directory_module_python_path = self.module_path_to_python_path(module_path)
        dst_directory = self.join_rst_path(self.python_path_to_path(directory_module_python_path))
        self._logger.info('Directory Module Name: {}'.format(directory_module_name))
        self._logger.info('Directory Module Python Path: {}'.format(directory_module_python_path))
        self._logger.info('Dest Path: {}'.format(dst_directory))

        if (python_files or sub_modules) and not os.path.exists(dst_directory):
            os.mkdir(dst_directory)

        # Generate a RST file per module
        module_names = []
        for file_name in python_files:
            module_name = self.filename_to_module(file_name)
            module_names.append(module_name)
            self._logger.info('  Module: {}'.format(module_name))
            rst = self._generate_rst_module(directory_module_python_path, module_name)
            rst_file_name = os.path.join(dst_directory, module_name + '.rst')
            with open(rst_file_name, 'w') as fh:
                fh.write(rst)

        # Generate the TOC RST file
        rst = self._generate_toc(
            directory_module_python_path,
            directory_module_name,
            sorted(module_names + sub_modules),
        )
        rst_file_name = os.path.join(os.path.dirname(dst_directory), directory_module_name + '.rst')
        with open(rst_file_name, 'w') as fh:
            fh.write(rst)

    ##############################################

    @classmethod
    def is_python_directory_module(cls, path):

        # path has __init__.py

        return os.path.exists(os.path.join(path, cls.INIT_FILE_NAME))

    ##############################################

    @classmethod
    def is_python_file(cls, file_name):

        return (
            file_name.endswith('.py') and
            file_name != cls.INIT_FILE_NAME and
            not file_name.startswith('flycheck') and
            not file_name.startswith('flymake') and
            file_name != 'parsetab.py'
        )

    ##############################################

    @staticmethod
    def path_to_python_path(path):

        return path.replace(os.path.sep, '.')

    ##############################################

    @staticmethod
    def python_path_to_path(python_path):

        return python_path.replace('.', os.path.sep)

    ##############################################

    @staticmethod
    def join_python_path(*args):

        return '.'.join(args)

    ##############################################

    @staticmethod
    def filename_to_module(file_name):

        return file_name[:-3] # suppress '.py'

    ##############################################

    def module_path_to_python_path(self, path):

        return self.path_to_python_path(self._root_module_name + path[len(self._root_module_path):])

    ##############################################

    def join_rst_path(self, path):

        return os.path.join(self._rst_directory, path)

    ##############################################

    def _generate_toc(self, directory_module_path, directory_module_name, submodules):

        return self._template_environment.render(
            'toc.jinja2',
            module=directory_module_path,
            title=directory_module_name,
            submodules=[os.path.join(directory_module_name, module_name) for module_name in submodules],
        )

    ##############################################

    def _generate_rst_module(self, module_path, module_name):

        return self._template_environment.render(
            'module.jinja2',
            title=module_name,
            module=self.join_python_path(module_path, module_name),
        )
