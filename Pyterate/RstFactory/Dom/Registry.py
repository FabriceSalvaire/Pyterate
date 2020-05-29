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

__all__ = ['MarkupRegistry']

####################################################################################################

import logging

####################################################################################################

_module_logger = logging.getLogger(__name__)

####################################################################################################

class MarkupRegistry(type):

    """Class to implement the markup registry"""

    _registry_ = []

    _command_map_ = {}
    _extensions_ = {}
    _markup_map_ = {}

    _enclosing_markups_ = []
    _markups_ = []

    _logger = _module_logger.getChild('MarkupRegistry')

    ##############################################

    # def __new__(cls, class_name, base_classes, attributes):
    #     return super().__new__(cls, class_name, base_classes, attributes)

    ##############################################

    def __init__(cls, class_name, base_classes, attributes):

        type.__init__(cls, class_name, base_classes, attributes)

        cls._registry_.append(cls)

        if hasattr(cls, 'MARKUP') and cls.MARKUP:
            MarkupRegistry._logger.info('Register {} for markup "{}"'.format(cls, cls.MARKUP))
            MarkupRegistry._markup_map_[cls.MARKUP] = cls
            if hasattr(cls, 'ENCLOSING_MARKUP'):
                array = MarkupRegistry._enclosing_markups_
            else:
                array = MarkupRegistry._markups_
            array.append(cls.MARKUP)
        elif hasattr(cls, 'COMMAND') and cls.COMMAND:
            MarkupRegistry._logger.info('Register {} for command "{}"'.format(cls, cls.COMMAND))
            MarkupRegistry._command_map_[cls.COMMAND] = cls
            if hasattr(cls, 'make_figure'):
                MarkupRegistry._extensions_[cls.COMMAND] = cls

    ##############################################

    @classmethod
    def is_valid_makup(cls, markup):
        return markup in cls._markups_

    @classmethod
    def is_valid_enclosing_makup(cls, markup):
        return markup in cls._enclosing_markups_

    @classmethod
    def markup_to_class(cls, markup):
        return cls._markup_map_[markup]

    @classmethod
    def command_to_class(cls, command):
        return cls._command_map_[command]

    @classmethod
    def commands(cls):
        return cls._command_map_.keys()

    @classmethod
    def extensions(cls):
        return cls._extensions_.values()

    ##############################################

    @classmethod
    def do_check_environment(cls):
        for cls in MarkupRegistry._registry_:
            if hasattr(cls, 'check_environment'):
                cls.check_environment()
            else:
                mangled_name = '_{}__check_environment'.format(cls.__name__)
                if hasattr(cls, mangled_name):
                    getattr(cls, mangled_name)()
