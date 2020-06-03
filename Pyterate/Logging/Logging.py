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
import logging.config
import os

import yaml

####################################################################################################

from ..Config import ConfigInstall as ConfigInstall

####################################################################################################

APPLICATION_NAME = 'Pyterate'
LOG_LEVEL_ENV = APPLICATION_NAME + 'LogLevel'

####################################################################################################

def setup_logging(application_name=APPLICATION_NAME, config_file=None):

    if config_file is None:
        config_file = ConfigInstall.Path.config_directory.joinpath(ConfigInstall.Logging.default_config_file)

    logging_config = yaml.load(open(config_file, 'r'), Loader=yaml.SafeLoader)

    if ConfigInstall.OS.on_linux:
        # Fixme: \033 is not interpreted in YAML
        formatter_config = logging_config['formatters']['ansi']['format']
        logging_config['formatters']['ansi']['format'] = formatter_config.replace('<ESC>', '\033')

    if ConfigInstall.OS.on_windows or ConfigInstall.OS.on_osx:
        formatter = 'simple'
    else:
        formatter = 'ansi'
    logging_config['handlers']['console']['formatter'] = formatter

    logging.config.dictConfig(logging_config)

    logger = logging.getLogger(application_name)
    if LOG_LEVEL_ENV in os.environ:
        numeric_level = getattr(logging, os.environ[LOG_LEVEL_ENV], None)
        logger.setLevel(numeric_level)

    return logger
