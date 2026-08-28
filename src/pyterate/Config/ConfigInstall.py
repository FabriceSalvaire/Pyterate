####################################################################################################
#
# Pyterate - Sphinx add-ons to create API documentation for Python projects
# Copyright (C) 2014 Fabrice Salvaire
# SPDX-License-Identifier: GPL-3.0-or-later
#
####################################################################################################

####################################################################################################

from pathlib import Path
import sys

####################################################################################################

class OsFactory:

    ##############################################

    def __init__(self):

        if sys.platform.startswith('linux'):
            self._name = 'linux'
        elif sys.platform.startswith('win'):
            self._name = 'windows'
        elif sys.platform.startswith('darwin'):
            self._name = 'osx'

    ##############################################

    @property
    def name(self):
        return self._name

    @property
    def on_linux(self):
        return self._name == 'linux'

    @property
    def on_windows(self):
        return self._name == 'windows'

    @property
    def on_osx(self):
        return self._name == 'osx'

OS = OsFactory()

####################################################################################################

class Path:

    config_directory = Path(__file__).parent

####################################################################################################

class Logging:

    default_config_file = 'logging.yml'
