####################################################################################################
#
# Pyterate - Sphinx add-ons to create API documentation for Python projects
# Copyright (C) 2017 Fabrice Salvaire
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

"""Classes to define RST Factory settings.

"""

####################################################################################################

import logging
import os
import re
import sys

from ..Template import TemplateEnvironment

####################################################################################################

_module_logger = logging.getLogger(__name__)

####################################################################################################

class LanguageSettings:

    """Class to define the language settings.

    Attention: You must have a trailing comma if a tuple ``()`` has only one element,
    e.g. ``('foo',)``, else use a list, e.g. ``['foo']``.

    """

    name = None

    # Filename settings
    extensions = () # e.g. '.py'
    excluded_file_patterns = (
        # these file should be flymake temporary file
        'flymake_.*',
        'flycheck_.*',
    )

    # Comment settings
    comment = None # main comment token, e.g. '#' '//'
    left_markup = None # markup is left_markup + markup + right_markup
    right_markup = None

    open_markup = '<'
    close_markup = '>'

    # Must fit Python, RST and LaTeX formulae
    opening_format_markup = '@<@'
    closing_format_markup = '@>@'
    escaped_opening_format_markup = '@@<<@@'
    escaped_closing_format_markup = '@@>>@@'

    # Pygments lexers
    lexer = 'none'
    error_lexer = 'none'
    console_lexer = 'none'

    # Execution settings
    jupyter_kernel = None # name of the kernel
    setup_code = '' # some codes to be executed first
    document_setup_code = '' # some codes to be executed first

    notebook_metadata = {
        'kernelspec': {
            'display_name': 'Python 3',
            'language': 'python',
            'name': 'python3'
        },
        'language_info': {
            # 'codemirror_mode': {
            #     'name': 'ipython',
            #     'version': 3
            # },
            'file_extension': '.py',
            'mimetype': 'text/x-python',
            'name': 'python',
            'nbconvert_exporter': 'python',
            'pygments_lexer': 'ipython3',
            'version': '{0.major}.{0.minor}.{0.micro}'.format(sys.version_info),
        }
    }

    ##############################################

    _logger = _module_logger.getChild('LanguageSettings')

    ##############################################

    @classmethod
    def enclose_markup(cls, markup):

        return cls.left_markup + markup + cls.right_markup

    ##############################################

    @classmethod
    def filename_match(cls, path):

        """Method to match a filename to a language handler.

        Return True if the file is taken.

        """

        for extension in cls.extensions:
            if path.endswith(extension):
                return cls.filename_filter(path)
        return False

    ##############################################

    @classmethod
    def filename_filter(cls, path):

        """Define a filename filter.

        Overwrite this method in subclass to define a custom filter.

        Return False if the file is excluded.

        """

        basename = os.path.basename(path)
        for pattern in cls.excluded_file_patterns:
            if re.match(pattern, basename):
                cls._logger.info("\nExclude '{}' for '{}'".format(basename, pattern))
                return False
        return True

    ##############################################

    @classmethod
    def rule_filter(cls, line):

        return False

####################################################################################################

class DefaultPython3Settings(LanguageSettings):

    """Python 3 settings"""

    name = 'Python 3'

    # Fixme: how to distinguish Python 2 ???
    extensions = ['.py']

    comment = '#'
    left_markup = '#'
    right_markup = '#'

    lexer = 'py3'
    error_lexer = 'pytb' # Fixme: py3con py3tb are unknown ???
    console_lexer = 'none'

    jupyter_kernel = 'python3'

    # Import some functions and define __file__ to the Python input path
    setup_code = '''
from Pyterate.RstFactory.FigureTools import *
'''
    document_setup_code = '''
__file__ = '{file}'
'''

    ##############################################

    @classmethod
    def rule_filter(cls, line):

        return (line.startswith('#'*10) or # long rule
                line.startswith(' '*4 + '#'*10)) # short rule

####################################################################################################

class DefaultRstFactorySettings:

    """Class to define the Rst Factory settings."""

    # Input path
    input_path = 'examples' # Path of the documents

    # RST paths
    rst_source_path = 'doc/sphinx/source' # Path of the RST source directory
    rst_directory = 'examples' # Relative path of the documents in the RST sources

    # Templates
    user_template_path = None # User template path

    # Flags
    show_counters = False # Show documents counters in toc
    run_code = False # Run code
    make_external_figure = False # Generate external figures
    force = False # Force the figure generation

    # List of LanguageSettings subclasses
    languages = (
        DefaultPython3Settings,
    )

    ##############################################

    _logger = _module_logger.getChild('RstFactorySettings')

    ##############################################

    def __init__(self):

        if self.user_template_path is None:
            user_template_path = os.path.realpath(os.path.join(self.input_path, 'pytrate-templates'))
            if os.path.exists(user_template_path):
                self.user_template_path = user_template_path

        template_path = os.path.join(os.path.dirname(__file__), 'templates')
        search_path = []
        if self.user_template_path:
            self._logger.info('\nUser template path: {}'.format(self.user_template_path))
            search_path.append(self.user_template_path)
        search_path.append(template_path)
        self._template_environment = TemplateEnvironment(search_path)

        # Fixme: handle ~
        self.input_path = os.path.realpath(self.input_path)

        self.rst_source_path = os.path.realpath(self.rst_source_path)
        self.rst_path = os.path.join(self.rst_source_path, self.rst_directory)

        self._logger.info("\nInput Path: " + self.input_path)
        self._logger.info("\nRST Path: " + self.rst_path)

    ##############################################

    @property
    def template_environment(self):
        return self._template_environment

    ##############################################

    def join_input_path(self, *args):
        return os.path.join(self.input_path, *args)

    def join_rst_path(self, *args):
        return os.path.join(self.rst_path, *args)

    ##############################################

    def relative_input_path(self, path):

        relative_path = os.path.relpath(path, self.input_path)
        if relative_path == '.':
            return ''
        else:
            return relative_path

    ##############################################

    def language_for(self, path):

        for language in self.languages:
            if language.filename_match(path):
                return language
        return None
