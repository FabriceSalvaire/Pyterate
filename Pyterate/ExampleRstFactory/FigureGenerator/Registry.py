####################################################################################################
#
# AutoSphinx - Sphinx add-ons to create API documentation for Python projects
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

class ExtensionMetaclass(type):

    __extensions__ = {}

    _logger = _module_logger.getChild('ExtensionMetaclass')

    ##############################################

    def __new__(cls, class_name, base_classes, attributes):
        return super().__new__(cls, class_name, base_classes, attributes)

    ##############################################

    def __init__(cls, class_name, base_classes, attributes):

        type.__init__(cls, class_name, base_classes, attributes)

        ExtensionMetaclass._logger.info('Register {} for {}'.format(cls, cls.__markup__))
        ExtensionMetaclass.__extensions__[cls.__markup__] = cls

    ##############################################

    @classmethod
    def extensions(cls):
        return tuple(cls.__extensions__.values())

    ##############################################

    @classmethod
    def extension_markups(cls):
        return list(cls.__extensions__.keys())

    ##############################################

    @classmethod
    def iter(cls):
        return cls.__extensions__.items()

    ##############################################

    @classmethod
    def extension(cls, markup):
        return cls.__extensions__[markup]
