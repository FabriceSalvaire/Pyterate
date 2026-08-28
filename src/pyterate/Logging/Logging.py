####################################################################################################
#
# Pyterate - Sphinx add-ons to create API documentation for Python projects
# Copyright (C) 2014 Fabrice Salvaire
# SPDX-License-Identifier: GPL-3.0-or-later
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
