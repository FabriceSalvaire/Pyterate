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

####################################################################################################

_module_logger = logging.getLogger(__name__)

####################################################################################################

class MarkupRegistry(type):

    """Class to implement the markup registry"""

    # Fixme: __xxx__

    __command_map__ = {}
    __extensions__ = {}
    __markup_map__ = {}

    __enclosing_markups__ = []
    __markups__ = []

    _logger = _module_logger.getChild('MarkupRegistry')

    ##############################################

    # def __new__(cls, class_name, base_classes, attributes):
    #     return super().__new__(cls, class_name, base_classes, attributes)

    ##############################################

    def __init__(cls, class_name, base_classes, attributes):

        type.__init__(cls, class_name, base_classes, attributes)

        if hasattr(cls, 'MARKUP') and cls.MARKUP:
            MarkupRegistry._logger.info('Register {} for markup "{}"'.format(cls, cls.MARKUP))
            MarkupRegistry.__markup_map__[cls.MARKUP] = cls
            if hasattr(cls, 'ENCLOSING_MARKUP'):
                array = MarkupRegistry.__enclosing_markups__
            else:
                array = MarkupRegistry.__markups__
            array.append(cls.MARKUP)
        elif hasattr(cls, 'COMMAND') and cls.COMMAND:
            MarkupRegistry._logger.info('Register {} for command "{}"'.format(cls, cls.COMMAND))
            MarkupRegistry.__command_map__[cls.COMMAND] = cls
            if hasattr(cls, 'make_figure'):
                MarkupRegistry.__extensions__[cls.COMMAND] = cls

    ##############################################

    @classmethod
    def is_valid_makup(cls, markup):
        return markup in cls.__markups__

    @classmethod
    def is_valid_enclosing_makup(cls, markup):
        return markup in cls.__enclosing_markups__

    @classmethod
    def markup_to_class(cls, markup):
        return cls.__markup_map__[markup]

    @classmethod
    def command_to_class(cls, command):
        return cls.__command_map__[command]

    @classmethod
    def commands(cls):
        return cls.__command_map__.keys()
